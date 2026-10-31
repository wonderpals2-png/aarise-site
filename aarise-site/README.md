# Aarise — marketing site

## Frontend
`frontend/index.html` is fully self-contained (HTML/CSS/JS, Google Fonts via CDN).
Open it directly in a browser, or serve it through the backend below.

## Backend
A small FastAPI app that serves the frontend and stores "Request a demo" leads in SQLite.

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Visit http://127.0.0.1:8000

- `POST /api/leads` — `{ "name": "...", "email": "...", "message": "..." }`
- `GET /api/leads` — list captured leads
