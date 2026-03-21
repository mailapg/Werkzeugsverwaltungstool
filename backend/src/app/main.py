# ============================================================
# main.py – Einstiegspunkt der FastAPI-Anwendung
#
# Hier wird die gesamte App zusammengebaut:
#   1. FastAPI-Instanz erstellen
#   2. CORS-Middleware konfigurieren (Frontend darf auf Backend zugreifen)
#   3. Statische Dateien (Werkzeugbilder) bereitstellen
#   4. Alle API-Router einbinden
# ============================================================

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from src.app.db.session import SessionLocal, engine
from src.app.db.base import Base
import src.app.models  # noqa: F401 – alle Modelle bei Base.metadata registrieren
from src.app.api.router import api_router
from src.app.auth.router import router as auth_router

# Ordner für hochgeladene Werkzeugbilder
STATIC_DIR = Path("static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Wird beim Start der Anwendung ausgeführt.
    - Erstellt alle Datenbanktabellen (falls nicht vorhanden)
    - Stellt sicher, dass der Ordner für Werkzeugbilder existiert
    """
    Base.metadata.create_all(bind=engine)
    (STATIC_DIR / "tool_images").mkdir(parents=True, exist_ok=True)
    yield


# FastAPI-App-Instanz erstellen
app = FastAPI(title="Werkzeugverwaltungstool API", version="0.1.0", lifespan=lifespan)

# CORS-Middleware: Erlaubt dem React-Frontend (Port 5173/5174) API-Anfragen zu stellen.
# Ohne diese Konfiguration würde der Browser alle Anfragen blockieren,
# da Backend (Port 8000) und Frontend (Port 5173) als unterschiedliche Ursprünge gelten.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,  # Cookies und Auth-Header erlauben
    allow_methods=["*"],     # GET, POST, PATCH, DELETE etc. erlauben
    allow_headers=["*"],     # Authorization-Header (JWT) erlauben
)

# Statische Dateien bereitstellen: Werkzeugbilder abrufbar unter /static/tool_images/
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Login/Logout-Endpunkte unter /auth/...
app.include_router(auth_router)

# Alle anderen API-Endpunkte unter /api/v1/...
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["System"])
def health():
    """Einfacher Healthcheck – prüft ob die App läuft."""
    return {"status": "ok"}


@app.get("/debug/db-check", tags=["System"])
def db_check():
    """Debug-Endpunkt – prüft ob die Datenbankverbindung funktioniert."""
    db = SessionLocal()
    try:
        db.execute(text("SELECT * FROM loans"))
        return {"ok": True, "db": "reachable"}
    finally:
        db.close()