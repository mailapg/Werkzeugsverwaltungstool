from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from src.app.db.session import SessionLocal, engine
from src.app.db.base import Base
import src.app.models  # noqa: F401 – register all models with Base.metadata
from src.app.api.router import api_router
from src.app.auth.router import router as auth_router

STATIC_DIR = Path("static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    (STATIC_DIR / "tool_images").mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Werkzeugverwaltungstool API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(auth_router)
app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}

@app.get("/debug/db-check", tags=["System"])
def db_check():
    db = SessionLocal()
    try:
        db.execute(text("SELECT * FROM loans"))
        return {"ok": True, "db": "reachable"}
    finally:
        db.close()