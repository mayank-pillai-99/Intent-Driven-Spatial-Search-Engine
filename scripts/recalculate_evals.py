import os
import glob
import pandas as pd
from sqlglot import parse_one
from sqlglot import expressions as exp
from tabulate import tabulate

def normalize_sql(sql: str) -> str:
    if not isinstance(sql, str):
        return ""
    sql = sql.replace("\n", " ").replace("\t", " ")
    sql = " ".join(sql.split())
    if sql.endswith(";"):
        sql = sql[:-1].strip()
    return sql

def extract_components(sql: str) -> dict:
    try:
        tree = parse_one(sql, dialect="postgres")
    except Exception as e:
        return {"error": str(e)}

    c = {
        "select_cols": set(), "from_tables": set(),
        "where_cols":  set(), "where_ops":   set(),
        "order_cols":  set(), "limit":       None,
        "spatial_funcs": set() # NEW! GeoSQL-Eval Spatial function tracker
    }
    
    if tree is None:
        return c

    for col   in tree.find_all(exp.Column): c["select_cols"].add(col.name.lower())
    for table in tree.find_all(exp.Table):  c["from_tables"].add(table.name.lower())

    # Extract PostGIS spatial functions
    for func in tree.find_all(exp.Anonymous):
        fname = func.name.lower()
        if fname.startswith("st_"):
            c["spatial_funcs"].add(fname)

    where = tree.find(exp.Where)
    if where:
        for col in where.find_all(exp.Column): c["where_cols"].add(col.name.lower())
        if where.find(exp.ILike): c["where_ops"].add("ilike")
        if where.find(exp.EQ):    c["where_ops"].add("eq")
        if where.find(exp.Is):    c["where_ops"].add("is_null")

    order = tree.find(exp.Order)
    if order:
        for col in order.find_all(exp.Column): c["order_cols"].add(col.name.lower())

    limit = tree.find(exp.Limit)
    if limit: c["limit"] = str(limit.expression)
    return c

def structural_score(gold_sql: str, pred_sql: str) -> dict:
    gold = extract_components(normalize_sql(gold_sql))
    pred = extract_components(normalize_sql(pred_sql))

    if "error" in gold or "error" in pred:
        return {
            "parse_error": True,
            "select_match": False, "from_match": False,
            "where_cols_match": False, "where_ops_match": False,
            "order_match": False, "limit_match": False,
            "spatial_func_match": False,
            "structural_score": 0.0,
        }

    checks = {
        "select_match":       gold["select_cols"]   == pred["select_cols"],
        "from_match":         gold["from_tables"]   == pred["from_tables"],
        "where_cols_match":   gold["where_cols"]    == pred["where_cols"],
        "where_ops_match":    gold["where_ops"]     == pred["where_ops"],
        "order_match":        gold["order_cols"]    == pred["order_cols"],
        "limit_match":        gold["limit"]         == pred["limit"],
        "spatial_func_match": gold["spatial_funcs"] == pred["spatial_funcs"],
    }
    return {
        "parse_error": False, **checks,
        "structural_score": round(sum(checks.values()) / len(checks), 3),
    }

def print_report(df: pd.DataFrame, report_file: str):
    import sys
    class Tee:
        def __init__(self, *files):
            self.files = files
        def write(self, obj):
            for f in self.files:
                f.write(obj)
                f.flush()
        def flush(self):
            for f in self.files:
                f.flush()

    f = open(report_file, "w", encoding="utf-8")
    original_stdout = sys.stdout
    sys.stdout = Tee(sys.stdout, f)

    try:
        total       = len(df)
        passed      = df["hybrid_pass"].sum()
        sem_only    = (df["verdict"] == "⚠️  SEM_ONLY").sum()
        struct_only = (df["verdict"] == "⚠️  STRUCT_ONLY").sum()
        failed      = (df["verdict"] == "❌ FAIL").sum()
        no_pred     = (df["verdict"] == "⚠️  NO_PRED").sum()

        print("\n" + "=" * 65)
        print("📊  HYBRID EVALUATION REPORT  v4.2 (Updated w/ Spatial Func Check)")
        print("=" * 65)
        print(f"  Total          : {total}")
        print(f"  ✅ PASS        : {passed}  ({100*passed/total:.1f}%)")
        print(f"  ❌ FAIL        : {failed}  ({100*failed/total:.1f}%)")
        print(f"  ⚠️  STRUCT_ONLY : {struct_only}")
        print(f"  ⚠️  SEM_ONLY    : {sem_only}")
        print(f"  ⚠️  NO_PRED     : {no_pred}")
        print(f"\n  Avg Struct Score  : {df['structural_score'].mean():.3f}")
        print(f"  Avg F1 Semantic   : {df['f1_score'].mean():.3f}")

        diff_order = ["easy", "medium", "hard", "extra", "extreme"]
        if "difficulty" in df.columns:
            diff_df = df[df["difficulty"].isin(diff_order)].copy()
            if not diff_df.empty:
                diff_df["difficulty"] = pd.Categorical(diff_df["difficulty"], categories=diff_order, ordered=True)
                print("\n── Per-Difficulty (Spider-style) ──────────────────────────")
                ds = diff_df.groupby("difficulty", observed=True).agg(
                    total=("id","count"), passed=("hybrid_pass","sum"),
                    avg_struct=("structural_score","mean"), avg_f1=("f1_score","mean"),
                ).reset_index()
                ds["pass_%"] = (ds["passed"] / ds["total"] * 100).round(1)
                print(tabulate(ds, headers="keys", tablefmt="rounded_outline", showindex=False))

        failures = df[df["hybrid_pass"] == False]
        if not failures.empty:
            print("\n── Failed / Warning Cases ─────────────────────────────────")
            for _, row in failures.iterrows():
                diff_str = f"[{row.get('difficulty', '')}]" if "difficulty" in row else ""
                print(f"\n  [{row['id']:02d}] {row['verdict']}  {diff_str}  {row.get('question', '')}")
                print(f"       GOLD    : {str(row['gold_sql'])[:110].strip()}")
                print(f"       PRED    : {(str(row['pred_sql']) or '(none)')[:110].strip()}")
                if "missing_names" in row and row['missing_names'] not in ('[]', ''):
                    print(f"       MISSING : {row['missing_names']}")
                if "extra_names" in row and row['extra_names'] not in ('[]', ''):
                    print(f"       EXTRA   : {row['extra_names']}")

        print("\n" + "=" * 65)
    finally:
        sys.stdout = original_stdout
        f.close()

def main():
    base_dir = "/Users/mayankpillai/Desktop/VISRI/PROJECT/evals"
    # Find all CSV files in the evals directory and its subdirectories
    csv_files = glob.glob(os.path.join(base_dir, "**", "eval_results_*.csv"), recursive=True)
    
    for csv_file in csv_files:
        print(f"Processing: {csv_file}")
        df = pd.read_csv(csv_file)
        
        # Ensure we have the required columns
        if "gold_sql" not in df.columns or "pred_sql" not in df.columns:
            print("  Skipping: Missing gold_sql or pred_sql columns")
            continue
            
        for index, row in df.iterrows():
            gold_sql = str(row["gold_sql"]) if pd.notna(row["gold_sql"]) else ""
            pred_sql = str(row["pred_sql"]) if pd.notna(row["pred_sql"]) else ""
            
            # Recalculate structural score
            struct_result = structural_score(gold_sql, pred_sql)
            
            # Update columns
            df.at[index, "structural_score"] = struct_result["structural_score"]
            df.at[index, "select_match"] = struct_result["select_match"]
            df.at[index, "from_match"] = struct_result["from_match"]
            df.at[index, "where_cols_match"] = struct_result["where_cols_match"]
            df.at[index, "where_ops_match"] = struct_result["where_ops_match"]
            df.at[index, "order_match"] = struct_result["order_match"]
            df.at[index, "limit_match"] = struct_result["limit_match"]
            df.at[index, "spatial_func_match"] = struct_result["spatial_func_match"]
            
            # Re-evaluate hybrid pass
            # Previous semantic match and F1 score are preserved
            s = struct_result["structural_score"]
            m = row["semantic_match"]
            
            if s >= 0.50 and m: verdict = "✅ PASS"
            elif s >= 0.50:       verdict = "⚠️  STRUCT_ONLY"
            elif m:               verdict = "⚠️  SEM_ONLY"
            else:                 verdict = "❌ FAIL"
            
            # Keep NO_PRED if it was already NO_PRED
            if row["verdict"] == "⚠️  NO_PRED":
                verdict = "⚠️  NO_PRED"
                
            df.at[index, "verdict"] = verdict
            df.at[index, "hybrid_pass"] = (verdict == "✅ PASS")

        # Save updated CSV
        df.to_csv(csv_file, index=False)
        print(f"  Updated CSV: {csv_file}")
        
        # Determine report txt filename
        report_file = csv_file.replace("eval_results_", "eval_report_").replace(".csv", ".txt")
        print_report(df, report_file)
        print(f"  Updated TXT: {report_file}")

if __name__ == "__main__":
    main()
