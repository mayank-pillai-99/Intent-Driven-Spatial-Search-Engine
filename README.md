# Intent-Driven Spatial Search Engine

This repository contains the codebase and research for the **Intent-Driven Spatial Search Engine**, a hybrid NL-to-SQL architecture that translates colloquial, multi-lingual conversational queries into executable PostGIS spatial logic.

By completely abandoning rigid keyword matching, this engine maps highly subjective human intents ("quiet place to read", "cheap and fast") into mathematically enforced geospatial bounding boxes.

---

## 🚀 The Architecture Stack

We have transitioned from cloud-reliant APIs to a **100% offline, local-GPU powered architecture** utilizing state-of-the-art open-weights models.

1. **Input & ASR Layer (SeamlessM4T v2 Large):**
   - Transcribes regional Indian spoken audio and translates it directly into English in a single step on the GPU.
   - Text queries in native scripts (e.g., Devanagari) or Romanized Hinglish are identified via `langdetect` and translated offline using the same Seamless model.

2. **Semantic Router (Qwen2.5-Coder 7B):**
   - A Front-Door Intent Router classifies incoming queries via Zero-Shot reasoning.
   - Non-spatial small talk (e.g., "Who are you?") bypasses the spatial database completely to prevent LLM hallucinations.

3. **Text-to-SQL Engine (Qwen2.5-Coder 7B):**
   - Translates English spatial intents into complex PostgreSQL/PostGIS syntax.
   - Automatically handles `ST_DWithin` calculations and complex multi-column mapping (e.g., matching "late night vegan" to `"opening_hours" ILIKE '%24/7%' AND "diet:vegan" = 'yes'`).

4. **Database (PostgreSQL + PostGIS):**
   - The UI supports dynamic geocoding via `osmnx` (Nominatim API). Type in any college or campus globally, and the backend automatically downloads a 2km radius of OpenStreetMap data to build the spatial database on the fly.

5. **Output Layer (Folium & SeamlessM4T TTS):**
   - Geographic coordinates are plotted dynamically using `geopandas` on an interactive `folium` map.
   - **Marker Clustering** dynamically groups overlapping Point of Interest (POI) pins.
   - Qwen2.5 natively generates a friendly text response in the user's original language, which is synthesized into spoken audio offline by **SeamlessM4T**.

---

## 📂 Repository Structure

The project has been restructured for clarity:

```text
VISRI_PROJECT/
├── docs/                      # Documentation and Final Reports
│   └── VISRI_Final_Report.tex # The comprehensive LaTeX thesis/report
├── scripts/                   # Data processing and generation tools
│   ├── build_db.py            # Local DB setup scripts
│   └── generate_datasets.py   # Synthesizing audio/text eval datasets
├── notebooks/                 # Jupyter Notebooks for testing and deployment
│   ├── Final.ipynb            # 🌟 The complete End-to-End Gradio UI Pipeline
│   ├── testers/               # Isolated testing files for various models (Sarvam, Whisper, etc.)
│   └── archive/               # Legacy notebooks and deprecated testing logic
├── evals/                     # Benchmark results and analysis artifacts
└── README.md                  # Project overview
```

---

## 🛠️ Key Engineering Guardrails

Because Large Language Models are prone to geographic hallucination, several physical guardrails are baked into the pipeline:

1. **Empty-DB Kill Switch:** If Qwen successfully generates a SQL query, but the database returns 0 rows (e.g., no skateparks within 500m), a Python intercept completely bypasses Qwen's standard generation and hard-returns a failure message. This guarantees the AI never invents fictitious locations.
2. **The "Library Bug" Fix:** A strict negative constraint enforces the AI to avoid mapping libraries to the `education` column, correcting a severe bias in baseline SQL models.
3. **Missing-Anchor Protection:** If a user says "closest cafe" but fails to specify *what* it is closest to, the prompt explicitly blocks `ST_DWithin` self-joins, preventing database-crashing recursive cross-joins.

---

## 🍏 How to Run (Apple Silicon Mac Local)

We have optimized the pipeline to run 100% locally on M-series Macs using `mlx-lm` and Apple Metal Performance Shaders (MPS).

1. **Install System Dependencies:**
   ```bash
   brew install postgresql postgis ffmpeg
   ```
2. **Setup Python Environment:**
   ```bash
   python3 -m venv visri_env
   source visri_env/bin/activate
   pip install torch torchvision torchaudio mlx-lm librosa transformers huggingface_hub gradio sentence-transformers psycopg2-binary shapely
   python -m ipykernel install --user --name=visri_env --display-name "Python (VISRI Environment)"
   ```
3. **Pre-cache the 4-Bit MLX Model** (to prevent Jupyter socket crashes during download):
   ```bash
   python -c "from mlx_lm import load; load('mlx-community/Qwen2.5-Coder-7B-Instruct-4bit')"
   ```
4. **Run the Interface:**
   - Open **`notebooks/Final MAC.ipynb`** in **VS Code** (highly recommended over the browser to handle progress bar outputs).
   - Select the `visri_env` Python kernel.
   - Run all cells to launch the Gradio UI!
   - **Step 1:** Enter a campus name and click "Map & Load Database".
   - **Step 2:** Ask spatial questions!

---

## 🖥️ How to Run (Google Colab / NVIDIA GPU)

1. Open **`notebooks/Final.ipynb`** in Google Colab or a local Jupyter environment equipped with an NVIDIA GPU (Minimum: T4 16GB VRAM).
2. Execute the cells to download the required weights for `Qwen2.5-Coder` (run in 4-bit quantization via BitsAndBytes) and `SeamlessM4T`.
3. Launch the Gradio cell at the bottom.
4. **Step 1:** Enter a campus name (e.g., "Stanford University") and click "Map & Load Database".
5. **Step 2:** Use text or the microphone to ask spatial questions in English, Hindi, Marathi, etc.

### Sample Test Queries
- **Pragmatic:** "Find a wheelchair accessible restaurant."
- **Spatial:** "Find a quiet place to read within 500 meters of the dormitory."
- **Frictional:** "I need something cheap and fast food place."
- **Multilingual:** "लहान मुलांसाठी खेळण्याची जागा कुठे आहे?" *(Where is a playground for kids?)*