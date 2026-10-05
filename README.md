# Vireo Audio — Support Intelligence

A small Streamlit tool for the Set A take-home.

## Key finding
Q2 2026 repeat-contact rate: **10.5%**.
Recommended target: **8.0%**, worth about **₹15,321/quarter**
at Q2 volume and policy contact costs.

## Run
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Optional AI narrative:
```text
OPENAI_API_KEY=...
OPENAI_MODEL=...
```

The deterministic tool works without a key.

## Included
- `app.py`
- `prompts.md`
- `memo_to_priya.md`
- `validation.md`
- `screen_recording_script.md`
- `submission_form_missing.md`
- `data/` with the supplied source files
- `category_summary.csv`

## Deliberate scope cuts
No RAG/vector DB, no agentic workflow, no LLM-based KPI calculation, and no
semantic clustering. The assignment asks for a reliable small tool, not a
platform.
