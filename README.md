# Contract Intelligence Platform (Django)

This repository now contains a fresh Django-based UI for the Contract RAG system.

Quick start (after activating your existing virtualenv):

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://localhost:8000 to access the web UI.

Notes:
- The RAG backend is in `src/` (reused from earlier work). Place your `.txt` contracts in `data/raw/` via the UI and use the upload button to rebuild the knowledge base.
- Keep your virtualenv `.venv` intact as requested.
