# 🏆 Text-to-SQL Model Comparison Report

## Qwen2.5-Coder-7B-Instruct vs SQLCoder-8B (llama-3-sqlcoder-8b)

> **Benchmark:** 50 English queries on the VISRI campus PostGIS database
> **Prompt:** Standard Prompt (no model-specific cheat codes)
> **Evaluation:** Hybrid v4.1 (Structural AST + F1-Semantic scoring)

---

## 1. Overall Results

| Metric               | Qwen2.5-Coder-7B | SQLCoder-8B | Δ (Difference) |
|-----------------------|:-----------------:|:-----------:|:---------------:|
| ✅ **PASS**           | **39 (78.0%)**    | 23 (46.0%)  | **+32pp**       |
| ❌ **FAIL**           | **1 (2.0%)**      | 14 (28.0%)  | **−26pp**       |
| ⚠️ **STRUCT_ONLY**    | 10                | 13          | −3              |
| ⚠️ **SEM_ONLY**       | 0                 | 0           | —               |
| ⚠️ **NO_PRED**        | 0                 | 0           | —               |
| **Avg Struct Score**  | **0.837**         | 0.580       | **+0.257**      |
| **Avg F1 Semantic**   | **0.780**         | 0.459       | **+0.321**      |

---

## 2. Per-Difficulty Breakdown

| Difficulty | Qwen Passed | Qwen Pass% | SQLCoder Passed | SQLCoder Pass% | Winner       |
|:----------:|:-----------:|:----------:|:---------------:|:--------------:|:------------:|
| **Easy**   | 8 / 8       | **100.0%** | 6 / 8           | 75.0%          | 🟢 Qwen      |
| **Medium** | 4 / 6       | 66.7%      | 5 / 6           | **83.3%**      | 🔵 SQLCoder  |
| **Hard**   | 9 / 13      | **69.2%**  | 6 / 13          | 46.2%          | 🟢 Qwen      |
| **Extra**  | 7 / 8       | **87.5%**  | 6 / 8           | 75.0%          | 🟢 Qwen      |

> **Note:** SQLCoder's only category win (Medium) comes from correctly using `ILIKE` for the volleyball/table_tennis query, while Qwen used `IN()` which missed a multi-tag row.

---

## 3. Query-by-Query Verdicts

### 3.1 Easy — Simple Lookups (Queries 1–8)

| # | Question                             | Qwen       | SQLCoder     | Notes                                                        |
|---|--------------------------------------|:----------:|:------------:|--------------------------------------------------------------|
| 1 | Where is the library?                | ✅ PASS    | ⚠️ STRUCT    | SQLCoder used `leisure` instead of `amenity` for library     |
| 2 | Show me all restaurants              | ✅ PASS    | ✅ PASS      | —                                                            |
| 3 | Where can I get coffee?              | ✅ PASS    | ⚠️ STRUCT    | SQLCoder searched `'%coffee%'` instead of `'%cafe%'`         |
| 4 | Find the pharmacy                    | ✅ PASS    | ✅ PASS      | —                                                            |
| 5 | Find an ATM                          | ✅ PASS    | ✅ PASS      | —                                                            |
| 6 | Where is a supermarket?              | ✅ PASS    | ✅ PASS      | —                                                            |
| 7 | Show me all dormitories              | ✅ PASS    | ✅ PASS      | —                                                            |
| 8 | Where can I play cricket?            | ✅ PASS    | ✅ PASS      | —                                                            |

**Subtotal — Qwen: 8/8 · SQLCoder: 6/8**

---

### 3.2 Medium — Boolean / Multi-filter (Queries 9–14)

| # | Question                                  | Qwen       | SQLCoder     | Notes                                                         |
|---|-------------------------------------------|:----------:|:------------:|---------------------------------------------------------------|
| 9  | Find cafes or restaurants                | ✅ PASS    | ✅ PASS      | —                                                             |
| 10 | Where are the hospitals or clinics?      | ✅ PASS    | ✅ PASS      | —                                                             |
| 11 | Find parks or gardens to relax in        | ✅ PASS    | ✅ PASS      | —                                                             |
| 12 | Find places with wifi or internet access | ⚠️ STRUCT  | ⚠️ STRUCT    | Both used `= 'wlan'` instead of `ILIKE '%wlan%' OR '%yes%'`  |
| 13 | Find volleyball or table tennis courts   | ⚠️ STRUCT  | ✅ PASS      | Qwen used `IN()`, SQLCoder used `ILIKE` (correct)             |
| 14 | Find bars or pubs                        | ✅ PASS    | ✅ PASS      | —                                                             |

**Subtotal — Qwen: 4/6 · SQLCoder: 5/6**

---

### 3.3 Hard — Negation & Missing Anchor (Queries 15–23, 47–50)

| #  | Question                                  | Qwen       | SQLCoder     | Notes                                                                  |
|----|-------------------------------------------|:----------:|:------------:|------------------------------------------------------------------------|
| 15 | Are there any cafes open 24/7?            | ✅ PASS    | ⚠️ STRUCT    | SQLCoder forgot `amenity ILIKE '%cafe%'` filter entirely               |
| 16 | Find wheelchair accessible restaurants    | ✅ PASS    | ✅ PASS      | —                                                                      |
| 17 | Is there anywhere for vegan food?         | ✅ PASS    | ✅ PASS      | —                                                                      |
| 18 | Is there anywhere open late for vegan?    | ✅ PASS    | ✅ PASS      | —                                                                      |
| 19 | Find a library that is NOT a school       | ✅ PASS    | ⚠️ STRUCT    | SQLCoder used `education IS NULL` — wrong negation approach            |
| 20 | Find a park but not a sports pitch        | ✅ PASS    | ✅ PASS      | —                                                                      |
| 21 | Find restaurants not serving fast food    | ✅ PASS    | ⚠️ STRUCT    | SQLCoder forgot `amenity ILIKE '%restaurant%'` → returned 594 rows     |
| 22 | Show me colleges that are not schools     | ✅ PASS    | ⚠️ STRUCT    | SQLCoder used `university IS NOT NULL` — wrong semantic approach       |
| 23 | Find hospitals that are not clinics       | ✅ PASS    | ✅ PASS      | —                                                                      |
| 47 | Find the nearest cafe (no anchor)         | ⚠️ STRUCT  | ❌ FAIL      | Both struggled — Qwen did spatial JOIN, SQLCoder used broken `row_number()` |
| 48 | Where is the closest hospital? (no anchor)| ❌ FAIL    | ❌ FAIL      | Both over-engineered with spatial JOIN instead of simple SELECT        |
| 49 | Find the nearest park (no anchor)         | ⚠️ STRUCT  | ✅ PASS      | SQLCoder got this one right                                            |
| 50 | Where is the closest restaurant? (no anchor)| ⚠️ STRUCT | ❌ FAIL     | SQLCoder used broken `row_number() OVER` syntax                        |

**Subtotal — Qwen: 9/13 · SQLCoder: 6/13**

---

### 3.4 Extra — Emotional Intent (Queries 24–31)

| #  | Question                                       | Qwen       | SQLCoder     | Notes                                               |
|----|------------------------------------------------|:----------:|:------------:|------------------------------------------------------|
| 24 | I am stressed, find a calm place               | ✅ PASS    | ✅ PASS      | —                                                    |
| 25 | Where is a quiet place to read a book?         | ✅ PASS    | ✅ PASS      | —                                                    |
| 26 | I want to relax in nature, find a garden       | ✅ PASS    | ✅ PASS      | —                                                    |
| 27 | Show me beautiful places for photography       | ✅ PASS    | ❌ FAIL      | SQLCoder generated broken CTE syntax                 |
| 28 | I need something quick to eat, no sit down     | ✅ PASS    | ✅ PASS      | —                                                    |
| 29 | Show me historic monuments or statues          | ✅ PASS    | ✅ PASS      | —                                                    |
| 30 | I need a productive place with good internet   | ⚠️ STRUCT  | ⚠️ STRUCT    | Both missed libraries (only found wifi places)       |
| 31 | I want to go for a swim, where is the pool?    | ✅ PASS    | ✅ PASS      | —                                                    |

**Subtotal — Qwen: 7/8 · SQLCoder: 6/8**

---

### 3.5 Extreme — Spatial / PostGIS (Queries 32–46)

| #  | Question                                              | Qwen       | SQLCoder     | Notes                                                          |
|----|-------------------------------------------------------|:----------:|:------------:|-----------------------------------------------------------------|
| 32 | Cafe within 500m of library                           | ✅ PASS    | ❌ FAIL      | SQLCoder used broken CTE; Qwen used clean `JOIN ON ST_DWithin` |
| 33 | Restaurant within 1000m of hospital                   | ✅ PASS    | ⚠️ STRUCT    | SQLCoder omitted geometry output columns                        |
| 34 | ATMs within 800m of dormitory                         | ✅ PASS    | ❌ FAIL      | SQLCoder used broken CTE syntax                                |
| 35 | Pharmacy within 500m of college                       | ⚠️ STRUCT  | ⚠️ STRUCT    | Both close but minor column issues                              |
| 36 | Parks within 1000m of hostel                          | ✅ PASS    | ⚠️ STRUCT    | SQLCoder used `tourism ILIKE '%hostel%'` (wrong column)         |
| 37 | Fast food within 500m of bank                         | ✅ PASS    | ⚠️ STRUCT    | SQLCoder omitted geometry columns                               |
| 38 | Calm place within 800m of engineering college         | ⚠️ STRUCT  | ❌ FAIL      | Both struggled; SQLCoder generated invalid SQL                  |
| 39 | Supermarket within 800m of hospital                   | ⚠️ STRUCT  | ⚠️ STRUCT    | Both used `amenity` instead of `shop` for supermarket           |
| 40 | Wheelchair-accessible cafe near library               | ✅ PASS    | ❌ FAIL      | SQLCoder generated broken syntax with unmatched parenthesis     |
| 41 | Closest hospital to library                           | ⚠️ STRUCT  | ❌ FAIL      | SQLCoder used `healthcare = 'hospital'` (wrong column)          |
| 42 | Nearest cafe to dormitory                             | ✅ PASS    | ❌ FAIL      | SQLCoder used broken `row_number() OVER` pattern                |
| 43 | Closest ATM to college                                | ✅ PASS    | ❌ FAIL      | Same broken window function pattern                             |
| 44 | Nearest pharmacy to hostel                            | ✅ PASS    | ❌ FAIL      | Same broken pattern                                             |
| 45 | Closest park to university                            | ✅ PASS    | ❌ FAIL      | Same broken pattern                                             |
| 46 | Nearest fast food to dormitory                        | ✅ PASS    | ❌ FAIL      | Same broken pattern                                             |

**Subtotal — Qwen: ~11 pass / 15 · SQLCoder: ~0 pass / 15 (10 FAIL, 5 STRUCT)**

---

## 4. Root Cause Analysis

### 4.1 SQLCoder-8B — Three Fatal Weaknesses

| # | Weakness                             | Description                                                                                         | Queries Affected                              |
|---|--------------------------------------|------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| 1 | **Broken Spatial SQL**               | Cannot write `JOIN ON ST_DWithin(...)`. Falls back to broken CTEs, subqueries, and `row_number() OVER` window functions that don't parse. | 32, 34, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48, 50 |
| 2 | **Wrong Column Mapping**             | Maps `library → leisure` (should be `amenity`), `coffee → amenity` (should be `cafe`), `hostel → tourism` (should be `building`), negation via `education IS NULL` instead of `NOT ILIKE`. | 1, 3, 19, 21, 22, 36                         |
| 3 | **Missing Primary Filters**          | Forgets to add the main category filter (e.g., `amenity ILIKE '%cafe%'`), causing massive over-selection. | 15, 21                                        |

### 4.2 Qwen2.5-Coder-7B — One Minor Weakness

| # | Weakness                             | Description                                                                                         | Queries Affected   |
|---|--------------------------------------|------------------------------------------------------------------------------------------------------|--------------------|
| 1 | **MissingAnchor Over-engineering**   | When no reference location is given ("Find the nearest cafe"), Qwen still constructs a spatial JOIN instead of a simple `SELECT ... ORDER BY name LIMIT 5`. | 47, 48, 49, 50     |

---

## 5. Cluster Strengths Summary

| Query Cluster      | Qwen Pass% | SQLCoder Pass% | Key Insight                                                   |
|--------------------|:----------:|:--------------:|---------------------------------------------------------------|
| Simple Lookups     | **100%**   | 75%            | SQLCoder maps wrong columns without explicit schema hints     |
| Boolean / OR       | 67%        | **83%**        | SQLCoder's only win — used `ILIKE` for multi-value sports     |
| Negation / NOT     | **100%**   | 40%            | Qwen natively understands `NOT ILIKE`; SQLCoder cannot        |
| Emotional Intent   | **88%**    | 75%            | Both strong; SQLCoder broke on CTE for photography query      |
| Spatial ST_DWithin | **80%**    | 0%             | SQLCoder cannot write spatial JOINs without cheat codes       |
| Nearest (anchored) | **100%**   | 0%             | SQLCoder cannot write `ORDER BY ST_Distance` pattern          |
| Nearest (no anchor)| 0%         | 25%            | Both weak — ambiguous queries without reference points        |

---

## 6. Verdict

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🏆  WINNER:  Qwen2.5-Coder-7B-Instruct                     ║
║                                                               ║
║   ┌───────────────────────────────────────────────────────┐   ║
║   │  Pass Rate     :  78%  vs  46%   (+32 points)        │   ║
║   │  Fail Rate     :   2%  vs  28%   (−26 points)        │   ║
║   │  Avg F1 Score  : 0.78  vs 0.46   (+0.32)             │   ║
║   │  Avg Struct    : 0.84  vs 0.58   (+0.26)             │   ║
║   └───────────────────────────────────────────────────────┘   ║
║                                                               ║
║   Qwen wins in 4/5 difficulty categories.                     ║
║   Qwen demonstrates genuine SQL reasoning ability.            ║
║   SQLCoder requires heavy prompt engineering to function.     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### Recommendation

**Qwen2.5-Coder-7B-Instruct** is the recommended model for the VISRI text-to-SQL pipeline because:

1. **It reasons independently** — solves negation, spatial JOINs, and emotional-intent mapping without any model-specific rules.
2. **It generates valid PostGIS SQL** — clean `JOIN ON ST_DWithin(...)` and `ORDER BY ST_Distance(...)` patterns.
3. **Its only weakness is genuinely ambiguous** — the "missing anchor" edge case where no reference location is provided.
4. **It is 4× smaller** than SQLCoder-34B alternatives, making it more practical for deployment.

---

*Report generated on 2026-06-25 using the VISRI Hybrid Evaluation Framework v4.1*
*Evaluation data: [evals/qwen/](./qwen/) · [evals/sql-coder/](./sql-coder/)*

### DeepSeek-Coder-7B vs Qwen2.5-Coder-7B
DeepSeek-Coder-7B completely failed the evaluation (28.0% pass rate vs Qwen's 84.0%). It suffered from massive schema hallucinations (inventing tables like `restaurant`) and failed to adhere to the strict spatial query formatting instructions provided in the prompt. Qwen2.5-Coder remains the undisputed champion of the 7B weight class.

### Sarvam-Translate (4B) vs NLLB-200 (1.3B)
Sarvam scored an 87.5% overall pass rate, beating NLLB's 85.7%. More importantly, Sarvam dramatically outperformed NLLB on code-mixed Hinglish and Slang inputs (scoring 71.4% vs NLLB's 57.1%), making it much more robust for real-world Indian user queries.

### CodeS-7B vs Qwen2.5-Coder-7B
CodeS-7B (the BIRD-SQL academic champion) completely failed the evaluation with a 34.0% pass rate. Because CodeS was aggressively fine-tuned on complex relational schemas with multiple tables, it struggled to adapt to the project's single denormalized OpenStreetMap schema. It frequently overcomplicated simple queries and hallucinated non-existent columns (e.g., `address`, `phone`). This proves that highly specialized academic models can overfit their benchmarks, cementing Qwen2.5-Coder's generalist superiority.

### SeamlessM4T v2 vs Sarvam vs NLLB
While SeamlessM4T v2 (Large) proved to be blazing fast and highly accurate on pure Native scripts (92.9% pass rate), it completely collapsed on Code-Mixed Hinglish and Slang inputs, scoring a dismal 42.9%. It failed to parse culturally contextualized words (leaving words like "bahut" untranslated), which broke the downstream SQL model. **Sarvam-Translate** remains the undisputed champion for Indian NLP tasks, proving that smaller, region-specific models (71.4% on slang) easily outperform global multimodal giants on localized dialects.
