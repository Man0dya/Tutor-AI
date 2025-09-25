# AI Tutoring System

A Streamlit-based multi-agent tutoring app with content generation, question setting, feedback evaluation, and knowledge-base search.

## Prereqs
- Python 3.10 or 3.11 (recommended)
- A Google Generative AI API key in the env var `GEMINI_API_KEY` (for content/questions/feedback). If not set, parts of the app will fall back to simple heuristics but AI features may fail.

## Setup
```powershell
# From the repo root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data (one-time)
python download_nltk_data.py

# Set your API key for this session (or use a .env file)
$env:GEMINI_API_KEY = "<your_api_key_here>"
```

Optionally create a `.env` file in the project root:
```
GEMINI_API_KEY=<your_api_key_here>
```



## Run
```powershell
streamlit run app.py
```

The app will start on http://localhost:8501 (or the port configured in `.streamlit/config.toml`).

## Notes
- Data persists under `data/sessions` as JSON files.
- If you see NLTK lookup errors (e.g., `punkt`), re-run `python download_nltk_data.py`.
- If Google API calls fail, ensure `google-genai` is installed and `GEMINI_API_KEY` is set.
