# Real-Time Analytics Dashboard

Event ingestion, event listing, aggregated metrics, synthetic demo data.

## Run locally

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

- API: http://127.0.0.1:8000
- OpenAPI docs: http://127.0.0.1:8000/docs
- Frontend: open `frontend/index.html`; if browser `file://` CORS restrictions apply, run `python -m http.server 5500 --directory frontend`.

## Included artifacts
Source code, frontend API playground, tests, Mermaid diagrams, requirements, database design notes, API spec, security notes, Docker configuration, manifest, and validation report.

## Limitations
This is a generated development prototype. Data is stored in memory, there is no authentication or authorization, and the UI is an API playground rather than a complete end-user application. Tests are included but have not been run in your target environment. No cloud deployment has been performed.
