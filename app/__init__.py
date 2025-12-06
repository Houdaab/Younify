"""
EEG Legitimacy Applications

Command-line tools and web applications for EEG analysis.

Scripts:
    human_check: Verify if EEG is from a human brain
    batch_score: Process multiple EEG files
    classify_states: Classify mental states
    dashboard: Interactive analysis dashboard
    server: FastAPI REST API

Usage:
    python -m app.human_check data/sample.csv
    python -m app.batch_score --data-dir data/
    streamlit run app/dashboard.py
    uvicorn app.server:app --reload
"""

__version__ = "1.0.0"
