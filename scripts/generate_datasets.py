import pandas as pd
import os

os.makedirs('evals', exist_ok=True)

# ====================================================================
# TEXT-TO-SQL BENCHMARK DATASET v3.0
# Campus: IIT Bombay, Mumbai
# Generated from live database discovery (1,610 named places)
# ====================================================================

queries = [

    # ─────────────────────────────────────────────────────────────────
    # CLUSTER 1: SIMPLE LOOKUPS (8 queries)
    # Tests: Basic single-column ILIKE filtering
    # ─────────────────────────────────────────────────────────────────
    {"id": 1, "cluster": "Simple", "difficulty": "easy",
     "question": "Where is the library?",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%library%' ORDER BY name ASC LIMIT 5;"},

    {"id": 2, "cluster": "Simple", "difficulty": "easy",
     "question": "Show me all restaurants.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%restaurant%' ORDER BY name ASC LIMIT 5;"},

    {"id": 3, "cluster": "Simple", "difficulty": "easy",
     "question": "Where can I get coffee?",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%cafe%' ORDER BY name ASC LIMIT 5;"},

    {"id": 4, "cluster": "Simple", "difficulty": "easy",
     "question": "Find the pharmacy.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%pharmacy%' ORDER BY name ASC LIMIT 5;"},

    {"id": 5, "cluster": "Simple", "difficulty": "easy",
     "question": "I need to withdraw cash, find an ATM.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%atm%' ORDER BY name ASC LIMIT 5;"},

    {"id": 6, "cluster": "Simple", "difficulty": "easy",
     "question": "Where is a supermarket?",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND shop ILIKE '%supermarket%' ORDER BY name ASC LIMIT 5;"},

    {"id": 7, "cluster": "Simple", "difficulty": "easy",
     "question": "Show me all dormitories on campus.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND building ILIKE '%dormitory%' ORDER BY name ASC LIMIT 5;"},

    {"id": 8, "cluster": "Simple", "difficulty": "easy",
     "question": "Where can I play cricket?",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND sport ILIKE '%cricket%' ORDER BY name ASC LIMIT 5;"},

    # ─────────────────────────────────────────────────────────────────
    # CLUSTER 2: MULTI-COLUMN BOOLEAN LOGIC (10 queries)
    # Tests: AND vs OR across same/different columns
    # ─────────────────────────────────────────────────────────────────
    {"id": 9, "cluster": "Boolean", "difficulty": "medium",
     "question": "Find cafes or restaurants.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND (amenity ILIKE '%cafe%' OR amenity ILIKE '%restaurant%') ORDER BY name ASC LIMIT 5;"},

    {"id": 10, "cluster": "Boolean", "difficulty": "medium",
     "question": "Where are the hospitals or clinics?",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND (amenity ILIKE '%hospital%' OR amenity ILIKE '%clinic%') ORDER BY name ASC LIMIT 5;"},

    {"id": 11, "cluster": "Boolean", "difficulty": "medium",
     "question": "Find parks or gardens to relax in.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND (leisure ILIKE '%park%' OR leisure ILIKE '%garden%') ORDER BY name ASC LIMIT 5;"},

    {"id": 12, "cluster": "Boolean", "difficulty": "medium",
     "question": "Find places with wifi or internet access.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND (internet_access ILIKE '%wlan%' OR internet_access ILIKE '%yes%') ORDER BY name ASC LIMIT 5;"},

    {"id": 13, "cluster": "Boolean", "difficulty": "medium",
     "question": "Find volleyball or table tennis courts.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND (sport ILIKE '%volleyball%' OR sport ILIKE '%table_tennis%') ORDER BY name ASC LIMIT 5;"},

    {"id": 14, "cluster": "Boolean", "difficulty": "medium",
     "question": "Find bars or pubs.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND (amenity ILIKE '%bar%' OR amenity ILIKE '%pub%') ORDER BY name ASC LIMIT 5;"},

    {"id": 15, "cluster": "Boolean", "difficulty": "hard",
     "question": "Are there any cafes open 24/7?",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%cafe%' AND opening_hours ILIKE '%24/7%' ORDER BY name ASC LIMIT 5;"},

    {"id": 16, "cluster": "Boolean", "difficulty": "hard",
     "question": "Find wheelchair accessible restaurants.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%restaurant%' AND wheelchair ILIKE '%yes%' ORDER BY name ASC LIMIT 5;"},

    {"id": 17, "cluster": "Boolean", "difficulty": "hard",
     "question": "Is there anywhere for vegan food?",
     "gold_sql": 'SELECT name FROM campus_places WHERE name IS NOT NULL AND name != \'nan\' AND (amenity ILIKE \'%restaurant%\' OR amenity ILIKE \'%cafe%\') AND "diet:vegan" = \'yes\' ORDER BY name ASC LIMIT 5;'},

    {"id": 18, "cluster": "Boolean", "difficulty": "hard",
     "question": "Is there anywhere open late for vegan food?",
     "gold_sql": 'SELECT name FROM campus_places WHERE name IS NOT NULL AND name != \'nan\' AND (amenity ILIKE \'%restaurant%\' OR amenity ILIKE \'%cafe%\') AND "diet:vegan" = \'yes\' AND opening_hours ILIKE \'%24/7%\' ORDER BY name ASC LIMIT 5;'},

    # ─────────────────────────────────────────────────────────────────
    # CLUSTER 3: NEGATION (5 queries)
    # Tests: NOT ILIKE exclusions
    # ─────────────────────────────────────────────────────────────────
    {"id": 19, "cluster": "Negation", "difficulty": "hard",
     "question": "Find a library that is NOT a school.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%library%' AND amenity NOT ILIKE '%school%' ORDER BY name ASC LIMIT 5;"},

    {"id": 20, "cluster": "Negation", "difficulty": "hard",
     "question": "Find a park but not a sports pitch.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND leisure ILIKE '%park%' AND leisure NOT ILIKE '%pitch%' ORDER BY name ASC LIMIT 5;"},

    {"id": 21, "cluster": "Negation", "difficulty": "hard",
     "question": "Find restaurants that do not serve fast food.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%restaurant%' AND amenity NOT ILIKE '%fast_food%' ORDER BY name ASC LIMIT 5;"},

    {"id": 22, "cluster": "Negation", "difficulty": "hard",
     "question": "Show me colleges that are not schools.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%college%' AND amenity NOT ILIKE '%school%' ORDER BY name ASC LIMIT 5;"},

    {"id": 23, "cluster": "Negation", "difficulty": "hard",
     "question": "Find hospitals that are not clinics.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%hospital%' AND amenity NOT ILIKE '%clinic%' ORDER BY name ASC LIMIT 5;"},

    # ─────────────────────────────────────────────────────────────────
    # CLUSTER 4: EMOTIONAL / PROXY MAPPING (8 queries)
    # Tests: Intent → Tag reasoning
    # ─────────────────────────────────────────────────────────────────
    {"id": 24, "cluster": "Emotional", "difficulty": "extra",
     "question": "I am so stressed, where can I find a calm place?",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND (leisure ILIKE '%park%' OR leisure ILIKE '%garden%' OR amenity ILIKE '%library%') ORDER BY name ASC LIMIT 5;"},

    {"id": 25, "cluster": "Emotional", "difficulty": "extra",
     "question": "Where is a quiet place to read a book?",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%library%' ORDER BY name ASC LIMIT 5;"},

    {"id": 26, "cluster": "Emotional", "difficulty": "extra",
     "question": "I want to relax in nature, find a garden.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND leisure ILIKE '%garden%' ORDER BY name ASC LIMIT 5;"},

    {"id": 27, "cluster": "Emotional", "difficulty": "extra",
     "question": "Show me beautiful places for photography.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND (tourism IS NOT NULL OR historic IS NOT NULL OR artwork_type IS NOT NULL) ORDER BY name ASC LIMIT 5;"},

    {"id": 28, "cluster": "Emotional", "difficulty": "extra",
     "question": "I need something quick to eat, no time to sit down.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND (amenity ILIKE '%fast_food%' OR takeaway ILIKE '%yes%') ORDER BY name ASC LIMIT 5;"},

    {"id": 29, "cluster": "Emotional", "difficulty": "extra",
     "question": "Show me historic monuments or statues for sightseeing.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND (historic ILIKE '%monument%' OR artwork_type ILIKE '%statue%') ORDER BY name ASC LIMIT 5;"},

    {"id": 30, "cluster": "Emotional", "difficulty": "extra",
     "question": "I need a productive place to study with good internet.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND (internet_access ILIKE '%wlan%' OR amenity ILIKE '%library%') ORDER BY name ASC LIMIT 5;"},

    {"id": 31, "cluster": "Emotional", "difficulty": "extra",
     "question": "I want to go for a swim, where is the pool?",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND leisure ILIKE '%swimming_pool%' ORDER BY name ASC LIMIT 5;"},

    # ─────────────────────────────────────────────────────────────────
    # CLUSTER 5: SPATIAL JOINS — ST_DWithin (9 queries)
    # Tests: Two-Pin radius search with self-join
    # ─────────────────────────────────────────────────────────────────
    {"id": 32, "cluster": "Spatial", "difficulty": "extreme",
     "question": "Find a cafe within 500 meters of the library.",
     "gold_sql": "SELECT target.geometry, target.name, target.amenity, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON ST_DWithin(target.geometry::geography, ref.geometry::geography, 500) WHERE target.name IS NOT NULL AND target.name != 'nan' AND target.amenity ILIKE '%cafe%' AND ref.amenity ILIKE '%library%' ORDER BY target.name ASC LIMIT 5;"},

    {"id": 33, "cluster": "Spatial", "difficulty": "extreme",
     "question": "Find a restaurant within 1000 meters of the hospital.",
     "gold_sql": "SELECT target.geometry, target.name, target.amenity, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON ST_DWithin(target.geometry::geography, ref.geometry::geography, 1000) WHERE target.name IS NOT NULL AND target.name != 'nan' AND target.amenity ILIKE '%restaurant%' AND (ref.amenity ILIKE '%hospital%' OR ref.building ILIKE '%hospital%') ORDER BY target.name ASC LIMIT 5;"},

    {"id": 34, "cluster": "Spatial", "difficulty": "extreme",
     "question": "Are there any ATMs within 800 meters of the dormitory?",
     "gold_sql": "SELECT target.geometry, target.name, target.amenity, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON ST_DWithin(target.geometry::geography, ref.geometry::geography, 800) WHERE target.name IS NOT NULL AND target.name != 'nan' AND target.amenity ILIKE '%atm%' AND ref.building ILIKE '%dormitory%' ORDER BY target.name ASC LIMIT 5;"},

    {"id": 35, "cluster": "Spatial", "difficulty": "extreme",
     "question": "Find a pharmacy within 500 meters of the college.",
     "gold_sql": "SELECT target.geometry, target.name, target.amenity, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON ST_DWithin(target.geometry::geography, ref.geometry::geography, 500) WHERE target.name IS NOT NULL AND target.name != 'nan' AND target.amenity ILIKE '%pharmacy%' AND ref.amenity ILIKE '%college%' ORDER BY target.name ASC LIMIT 5;"},

    {"id": 36, "cluster": "Spatial", "difficulty": "extreme",
     "question": "Find parks within 1000 meters of the hostel.",
     "gold_sql": "SELECT target.geometry, target.name, target.leisure, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON ST_DWithin(target.geometry::geography, ref.geometry::geography, 1000) WHERE target.name IS NOT NULL AND target.name != 'nan' AND target.leisure ILIKE '%park%' AND ref.tourism ILIKE '%hostel%' ORDER BY target.name ASC LIMIT 5;"},

    {"id": 37, "cluster": "Spatial", "difficulty": "extreme",
     "question": "Find fast food within 500 meters of the bank.",
     "gold_sql": "SELECT target.geometry, target.name, target.amenity, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON ST_DWithin(target.geometry::geography, ref.geometry::geography, 500) WHERE target.name IS NOT NULL AND target.name != 'nan' AND target.amenity ILIKE '%fast_food%' AND ref.amenity ILIKE '%bank%' ORDER BY target.name ASC LIMIT 5;"},

    {"id": 38, "cluster": "Spatial", "difficulty": "extreme",
     "question": "I am stressed, is there a calm place within 800 meters of the engineering college?",
     "gold_sql": "SELECT target.geometry, target.name, target.amenity, target.leisure, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON ST_DWithin(target.geometry::geography, ref.geometry::geography, 800) WHERE target.name IS NOT NULL AND target.name != 'nan' AND (target.amenity ILIKE '%library%' OR target.leisure ILIKE '%park%' OR target.natural ILIKE '%water%') AND (ref.name ILIKE '%engineering%' OR ref.building ILIKE '%college%') ORDER BY target.name ASC LIMIT 5;"},

    {"id": 39, "cluster": "Spatial", "difficulty": "extreme",
     "question": "Find a supermarket within 800 meters of the hospital.",
     "gold_sql": "SELECT target.geometry, target.name, target.shop, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON ST_DWithin(target.geometry::geography, ref.geometry::geography, 800) WHERE target.name IS NOT NULL AND target.name != 'nan' AND target.shop ILIKE '%supermarket%' AND (ref.amenity ILIKE '%hospital%' OR ref.building ILIKE '%hospital%') ORDER BY target.name ASC LIMIT 5;"},

    {"id": 40, "cluster": "Spatial", "difficulty": "extreme",
     "question": "Where is the closest wheelchair-accessible cafe to the library?",
     "gold_sql": "SELECT target.geometry, target.name, target.amenity, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON 1=1 WHERE target.name IS NOT NULL AND target.name != 'nan' AND target.amenity ILIKE '%cafe%' AND target.wheelchair ILIKE '%yes%' AND ref.amenity ILIKE '%library%' ORDER BY ST_Distance(target.geometry::geography, ref.geometry::geography) ASC LIMIT 1;"},

    # ─────────────────────────────────────────────────────────────────
    # CLUSTER 6: NEAREST NEIGHBOR — ST_Distance (6 queries)
    # Tests: Distance calculation + LIMIT 1
    # ─────────────────────────────────────────────────────────────────
    {"id": 41, "cluster": "Nearest", "difficulty": "extreme",
     "question": "Where is the closest hospital to the library?",
     "gold_sql": "SELECT target.geometry, target.name, target.amenity, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON 1=1 WHERE target.name IS NOT NULL AND target.name != 'nan' AND target.amenity ILIKE '%hospital%' AND ref.amenity ILIKE '%library%' ORDER BY ST_Distance(target.geometry::geography, ref.geometry::geography) ASC LIMIT 1;"},

    {"id": 42, "cluster": "Nearest", "difficulty": "extreme",
     "question": "Find the nearest cafe to the dormitory.",
     "gold_sql": "SELECT target.geometry, target.name, target.amenity, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON 1=1 WHERE target.name IS NOT NULL AND target.name != 'nan' AND target.amenity ILIKE '%cafe%' AND ref.building ILIKE '%dormitory%' ORDER BY ST_Distance(target.geometry::geography, ref.geometry::geography) ASC LIMIT 1;"},

    {"id": 43, "cluster": "Nearest", "difficulty": "extreme",
     "question": "What is the closest ATM to the college?",
     "gold_sql": "SELECT target.geometry, target.name, target.amenity, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON 1=1 WHERE target.name IS NOT NULL AND target.name != 'nan' AND target.amenity ILIKE '%atm%' AND ref.amenity ILIKE '%college%' ORDER BY ST_Distance(target.geometry::geography, ref.geometry::geography) ASC LIMIT 1;"},

    {"id": 44, "cluster": "Nearest", "difficulty": "extreme",
     "question": "Where is the nearest pharmacy to the hostel?",
     "gold_sql": "SELECT target.geometry, target.name, target.amenity, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON 1=1 WHERE target.name IS NOT NULL AND target.name != 'nan' AND target.amenity ILIKE '%pharmacy%' AND ref.tourism ILIKE '%hostel%' ORDER BY ST_Distance(target.geometry::geography, ref.geometry::geography) ASC LIMIT 1;"},

    {"id": 45, "cluster": "Nearest", "difficulty": "extreme",
     "question": "Find the closest park to the university.",
     "gold_sql": "SELECT target.geometry, target.name, target.leisure, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON 1=1 WHERE target.name IS NOT NULL AND target.name != 'nan' AND target.leisure ILIKE '%park%' AND ref.amenity ILIKE '%university%' ORDER BY ST_Distance(target.geometry::geography, ref.geometry::geography) ASC LIMIT 1;"},

    {"id": 46, "cluster": "Nearest", "difficulty": "extreme",
     "question": "Find the nearest fast food to the dormitory.",
     "gold_sql": "SELECT target.geometry, target.name, target.amenity, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON 1=1 WHERE target.name IS NOT NULL AND target.name != 'nan' AND target.amenity ILIKE '%fast_food%' AND ref.building ILIKE '%dormitory%' ORDER BY ST_Distance(target.geometry::geography, ref.geometry::geography) ASC LIMIT 1;"},

    # ─────────────────────────────────────────────────────────────────
    # CLUSTER 7: MISSING ANCHOR — No Reference Point (4 queries)
    # Tests: The new "Missing Anchor" rule. Model must NOT use
    #        ST_Distance/JOIN when no reference location is given.
    # ─────────────────────────────────────────────────────────────────
    {"id": 47, "cluster": "MissingAnchor", "difficulty": "hard",
     "question": "Find the nearest cafe.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%cafe%' ORDER BY name ASC LIMIT 5;"},

    {"id": 48, "cluster": "MissingAnchor", "difficulty": "hard",
     "question": "Where is the closest hospital?",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%hospital%' ORDER BY name ASC LIMIT 5;"},

    {"id": 49, "cluster": "MissingAnchor", "difficulty": "hard",
     "question": "Find the nearest park.",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND leisure ILIKE '%park%' ORDER BY name ASC LIMIT 5;"},

    {"id": 50, "cluster": "MissingAnchor", "difficulty": "hard",
     "question": "Where is the closest restaurant?",
     "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%restaurant%' ORDER BY name ASC LIMIT 5;"},
]

# ─────────────────────────────────────────────────────────────────
# SAVE TO CSV
# ─────────────────────────────────────────────────────────────────
df = pd.DataFrame(queries)
df.to_csv('evals/sql_benchmark_v3.csv', index=False)

print(f"✅ Generated {len(df)} queries across {df['cluster'].nunique()} clusters!")
print(f"\n📊 Breakdown:")
print(df.groupby(['cluster', 'difficulty']).size().to_string())
print(f"\n💾 Saved to: evals/sql_benchmark_v3.csv")
