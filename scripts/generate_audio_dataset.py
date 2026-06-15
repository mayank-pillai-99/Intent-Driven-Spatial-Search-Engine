import os
import pandas as pd
from gtts import gTTS
import time

def generate_audio_dataset(csv_path="evals/translation_benchmark_v1.csv", output_dir="evals/audio_dataset"):
    print("🎙️ Starting Synthetic Audio Generation Pipeline...")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created directory: {output_dir}")

    # Map your dataset languages to gTTS language codes
    # gTTS supports many Indian languages out of the box!
    lang_code_map = {
        "english": "en",
        "hindi": "hi",
        "marathi": "mr",
        "tamil": "ta",
        "telugu": "te",
        "punjabi": "pa",
        "multi": "hi" # For Hinglish/Slang, we fall back to Hindi voice engine
    }

    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"❌ Could not find {csv_path}. Make sure it is in the current directory.")
        return

    total = len(df)
    success = 0

    print(f"⏳ Generating {total} audio files...\n")

    for index, row in df.iterrows():
        q_id = row['id']
        language = str(row['language']).lower()
        dialect = str(row['dialect']).lower()
        text = str(row['translated_question'])
        
        # Get correct language code
        lang_code = lang_code_map.get(language, "hi")

        # Create a clean, descriptive filename
        # Format: 01_hindi_native.mp3
        safe_lang = language.replace(" ", "_")
        safe_dialect = dialect.replace(" ", "_")
        filename = f"{q_id:02d}_{safe_lang}_{safe_dialect}.mp3"
        filepath = os.path.join(output_dir, filename)

        try:
            # Skip if file already exists
            if os.path.exists(filepath):
                print(f"⏭️ Skipping {filename} (Already exists)")
                continue

            # Generate TTS
            tts = gTTS(text=text, lang=lang_code, slow=False)
            tts.save(filepath)
            
            print(f"✅ Created: {filename} ({lang_code}) -> '{text[:30]}...'")
            success += 1
            
            # Sleep slightly to avoid hitting API rate limits
            time.sleep(1.0)
            
        except Exception as e:
            print(f"⚠️ Error generating {filename}: {e}")

    print("\n" + "="*50)
    print(f"🎉 Complete! Successfully generated {success} new audio files.")
    print(f"📂 They are saved in the '{output_dir}' directory.")
    print("="*50)

if __name__ == "__main__":
    generate_audio_dataset()
