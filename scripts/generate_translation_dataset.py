import pandas as pd
import os

os.makedirs('evals', exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# BASE QUESTIONS FROM SQL BENCHMARK v3
# We select 7 highly distinct questions covering different PostGIS logic.
# ─────────────────────────────────────────────────────────────────────────────
base_queries = {
    1: {"cluster": "Simple", "difficulty": "easy", "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%library%' ORDER BY name ASC LIMIT 5;"},
    9: {"cluster": "Boolean", "difficulty": "medium", "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND (amenity ILIKE '%cafe%' OR amenity ILIKE '%restaurant%') ORDER BY name ASC LIMIT 5;"},
    24: {"cluster": "Emotional", "difficulty": "extra", "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND (leisure ILIKE '%park%' OR leisure ILIKE '%garden%' OR amenity ILIKE '%library%') ORDER BY name ASC LIMIT 5;"},
    32: {"cluster": "Spatial", "difficulty": "extreme", "gold_sql": "SELECT target.geometry, target.name, target.amenity, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON ST_DWithin(target.geometry::geography, ref.geometry::geography, 500) WHERE target.name IS NOT NULL AND target.name != 'nan' AND target.amenity ILIKE '%cafe%' AND ref.amenity ILIKE '%library%' ORDER BY target.name ASC LIMIT 5;"},
    42: {"cluster": "Nearest", "difficulty": "extreme", "gold_sql": "SELECT target.geometry, target.name, target.amenity, ref.geometry AS ref_geom, ref.name AS ref_name FROM campus_places target JOIN campus_places ref ON 1=1 WHERE target.name IS NOT NULL AND target.name != 'nan' AND target.amenity ILIKE '%cafe%' AND ref.building ILIKE '%dormitory%' ORDER BY ST_Distance(target.geometry::geography, ref.geometry::geography) ASC LIMIT 1;"},
    47: {"cluster": "MissingAnchor", "difficulty": "hard", "gold_sql": "SELECT name FROM campus_places WHERE name IS NOT NULL AND name != 'nan' AND amenity ILIKE '%cafe%' ORDER BY name ASC LIMIT 5;"},
}

# ─────────────────────────────────────────────────────────────────────────────
# LINGUISTIC MATRIX (Translations & Transliterations)
# ─────────────────────────────────────────────────────────────────────────────
translations = [
    # --- ID 1: Where is the library? ---
    {"id": 1, "base_question": "Where is the library?", "language": "English", "script_type": "Native", "input_text": "Where is the library?"},
    {"id": 1, "base_question": "Where is the library?", "language": "Hindi", "script_type": "Native", "input_text": "लाइब्रेरी कहाँ है?"},
    {"id": 1, "base_question": "Where is the library?", "language": "Marathi", "script_type": "Native", "input_text": "ग्रंथालय कुठे आहे?"},
    {"id": 1, "base_question": "Where is the library?", "language": "Telugu", "script_type": "Native", "input_text": "లైబ్రరీ ఎక్కడ ఉంది?"},
    {"id": 1, "base_question": "Where is the library?", "language": "Tamil", "script_type": "Native", "input_text": "நூலகம் எங்கே இருக்கிறது?"},
    {"id": 1, "base_question": "Where is the library?", "language": "Hindi", "script_type": "Romanized", "input_text": "library kahan hai?"},
    {"id": 1, "base_question": "Where is the library?", "language": "Tamil", "script_type": "Romanized", "input_text": "library engay irukku?"},
    {"id": 1, "base_question": "Where is the library?", "language": "Multi", "script_type": "Slang", "input_text": "bhai campus me library kidhar milegi?"},

    # --- ID 9: Find cafes or restaurants. ---
    {"id": 9, "base_question": "Find cafes or restaurants.", "language": "English", "script_type": "Native", "input_text": "Find cafes or restaurants."},
    {"id": 9, "base_question": "Find cafes or restaurants.", "language": "Hindi", "script_type": "Native", "input_text": "कैफे या रेस्टोरेंट खोजें।"},
    {"id": 9, "base_question": "Find cafes or restaurants.", "language": "Marathi", "script_type": "Native", "input_text": "कॅफे किंवा रेस्टॉरंट शोधा."},
    {"id": 9, "base_question": "Find cafes or restaurants.", "language": "Telugu", "script_type": "Native", "input_text": "కేఫ్‌లు లేదా రెస్టారెంట్‌లను కనుగొనండి."},
    {"id": 9, "base_question": "Find cafes or restaurants.", "language": "Tamil", "script_type": "Native", "input_text": "கஃபேக்கள் அல்லது உணவகங்களை கண்டுபிடி."},
    {"id": 9, "base_question": "Find cafes or restaurants.", "language": "Hindi", "script_type": "Romanized", "input_text": "cafe ya restaurant dhundho."},
    {"id": 9, "base_question": "Find cafes or restaurants.", "language": "Multi", "script_type": "Slang", "input_text": "koi khane peene ki jagah batao, cafe waghera"},

    # --- ID 24: I am so stressed, where can I find a calm place? ---
    {"id": 24, "base_question": "I am so stressed, where can I find a calm place?", "language": "English", "script_type": "Native", "input_text": "I am so stressed, where can I find a calm place?"},
    {"id": 24, "base_question": "I am so stressed, where can I find a calm place?", "language": "Hindi", "script_type": "Native", "input_text": "मैं बहुत तनाव में हूँ, मुझे शांत जगह कहाँ मिलेगी?"},
    {"id": 24, "base_question": "I am so stressed, where can I find a calm place?", "language": "Marathi", "script_type": "Native", "input_text": "मी खूप तणावात आहे, मला शांत जागा कुठे मिळेल?"},
    {"id": 24, "base_question": "I am so stressed, where can I find a calm place?", "language": "Telugu", "script_type": "Native", "input_text": "నేను చాలా ఒత్తిడిలో ఉన్నాను, ప్రశాంతమైన ప్రదేశం ఎక్కడ దొరుకుతుంది?"},
    {"id": 24, "base_question": "I am so stressed, where can I find a calm place?", "language": "Tamil", "script_type": "Native", "input_text": "நான் மிகவும் மன அழுத்தத்தில் இருக்கிறேன், அமைதியான இடம் எங்கே கிடைக்கும்?"},
    {"id": 24, "base_question": "I am so stressed, where can I find a calm place?", "language": "Hindi", "script_type": "Romanized", "input_text": "main bahut stressed hoon, koi shant jagah kahan milegi?"},
    {"id": 24, "base_question": "I am so stressed, where can I find a calm place?", "language": "Multi", "script_type": "Slang", "input_text": "yaar dimaag kharab ho raha hai, koi shanti wali jagah bata de"},

    # --- ID 32: Find a cafe within 500 meters of the library. ---
    {"id": 32, "base_question": "Find a cafe within 500 meters of the library.", "language": "English", "script_type": "Native", "input_text": "Find a cafe within 500 meters of the library."},
    {"id": 32, "base_question": "Find a cafe within 500 meters of the library.", "language": "Hindi", "script_type": "Native", "input_text": "लाइब्रेरी के 500 मीटर के भीतर एक कैफे खोजें।"},
    {"id": 32, "base_question": "Find a cafe within 500 meters of the library.", "language": "Marathi", "script_type": "Native", "input_text": "ग्रंथालयाच्या ५०० मीटर अंतरावर कॅफे शोधा."},
    {"id": 32, "base_question": "Find a cafe within 500 meters of the library.", "language": "Telugu", "script_type": "Native", "input_text": "లైబ్రరీకి 500 మీటర్ల లోపు కేఫ్‌ని కనుగొనండి."},
    {"id": 32, "base_question": "Find a cafe within 500 meters of the library.", "language": "Tamil", "script_type": "Native", "input_text": "நூலகத்தின் 500 மீட்டருக்குள் ஒரு கஃபேவை கண்டுபிடி."},
    {"id": 32, "base_question": "Find a cafe within 500 meters of the library.", "language": "Hindi", "script_type": "Romanized", "input_text": "library ke 500 meter ke andar ek cafe batao."},
    {"id": 32, "base_question": "Find a cafe within 500 meters of the library.", "language": "Multi", "script_type": "Slang", "input_text": "library ke aas paas 500m me koi chai ki tapri hai kya?"},

    # --- ID 42: Find the nearest cafe to the dormitory. ---
    {"id": 42, "base_question": "Find the nearest cafe to the dormitory.", "language": "English", "script_type": "Native", "input_text": "Find the nearest cafe to the dormitory."},
    {"id": 42, "base_question": "Find the nearest cafe to the dormitory.", "language": "Hindi", "script_type": "Native", "input_text": "छात्रावास के सबसे करीब कैफे खोजें।"},
    {"id": 42, "base_question": "Find the nearest cafe to the dormitory.", "language": "Marathi", "script_type": "Native", "input_text": "वसतिगृहाच्या सर्वात जवळचा कॅफे शोधा."},
    {"id": 42, "base_question": "Find the nearest cafe to the dormitory.", "language": "Telugu", "script_type": "Native", "input_text": "హాస్టల్‌కు అత్యంత సమీపంలో ఉన్న కేఫ్‌ని కనుగొనండి."},
    {"id": 42, "base_question": "Find the nearest cafe to the dormitory.", "language": "Tamil", "script_type": "Native", "input_text": "விடுதிக்கு மிக அருகில் உள்ள கஃபேவை கண்டுபிடி."},
    {"id": 42, "base_question": "Find the nearest cafe to the dormitory.", "language": "Hindi", "script_type": "Romanized", "input_text": "hostel ke sabse paas wala cafe batao."},
    {"id": 42, "base_question": "Find the nearest cafe to the dormitory.", "language": "Multi", "script_type": "Slang", "input_text": "hostel ke nazdeek sabse paas wali tapri kidhar hai?"},

    # --- ID 47: Find the nearest cafe. ---
    {"id": 47, "base_question": "Find the nearest cafe.", "language": "English", "script_type": "Native", "input_text": "Find the nearest cafe."},
    {"id": 47, "base_question": "Find the nearest cafe.", "language": "Hindi", "script_type": "Native", "input_text": "सबसे नज़दीकी कैफे खोजें।"},
    {"id": 47, "base_question": "Find the nearest cafe.", "language": "Marathi", "script_type": "Native", "input_text": "सर्वात जवळचा कॅफे शोधा."},
    {"id": 47, "base_question": "Find the nearest cafe.", "language": "Telugu", "script_type": "Native", "input_text": "సమీపంలోని కేఫ్‌ని కనుగొనండి."},
    {"id": 47, "base_question": "Find the nearest cafe.", "language": "Tamil", "script_type": "Native", "input_text": "அருகில் உள்ள கஃபேவை கண்டுபிடி."},
    {"id": 47, "base_question": "Find the nearest cafe.", "language": "Hindi", "script_type": "Romanized", "input_text": "sabse paas ka cafe dhundho."},
    {"id": 47, "base_question": "Find the nearest cafe.", "language": "Multi", "script_type": "Slang", "input_text": "aas paas koi cafe hai kya bata de bhai."},
]

def generate_csv():
    records = []
    for t in translations:
        base = base_queries[t["id"]]
        records.append({
            "id": t["id"],
            "cluster": base["cluster"],
            "difficulty": base["difficulty"],
            "base_question": t["base_question"],
            "language": t["language"],
            "script_type": t["script_type"],
            "input_text": t["input_text"],
            "gold_sql": base["gold_sql"]
        })
    
    df = pd.DataFrame(records)
    out_path = 'evals/translation_benchmark_v1.csv'
    df.to_csv(out_path, index=False)
    
    print(f"✅ Generated Translation Benchmark Dataset!")
    print(f"Total translated queries: {len(df)}")
    print(f"Languages included: {df['language'].unique()}")
    print(f"Saved to: {out_path}")

if __name__ == "__main__":
    generate_csv()
