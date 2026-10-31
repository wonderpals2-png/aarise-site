"""
Aarise marketing site backend.

Serves the static landing page and exposes a single endpoint for capturing
"Request a demo" leads to a local SQLite database. Kept deliberately small —
this is a companion to the site, not the Aarise device backend.
"""
from pathlib import Path
from datetime import datetime
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
DB_PATH = BASE_DIR / "leads.db"

app = FastAPI(title="Aarise Site")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


@app.on_event("startup")
def on_startup():
    init_db()


class LeadIn(BaseModel):
    name: str
    email: EmailStr
    message: str | None = None


class LeadOut(LeadIn):
    id: int
    created_at: str


@app.post("/api/leads", response_model=LeadOut)
def create_lead(lead: LeadIn):
    conn = get_db()
    created_at = datetime.utcnow().isoformat()
    cur = conn.execute(
        "INSERT INTO leads (name, email, message, created_at) VALUES (?, ?, ?, ?)",
        (lead.name, lead.email, lead.message, created_at),
    )
    conn.commit()
    lead_id = cur.lastrowid
    conn.close()
    return LeadOut(id=lead_id, created_at=created_at, **lead.dict())


@app.get("/api/leads", response_model=list[LeadOut])
def list_leads():
    conn = get_db()
    rows = conn.execute("SELECT * FROM leads ORDER BY id DESC").fetchall()
    conn.close()
    return [LeadOut(**dict(row)) for row in rows]


@app.get("/")
def serve_index():
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path)


# Serve any other static assets placed in /frontend (images, etc.)
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")
