from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from src.app.db.session import SessionLocal, engine
from src.app.db.base import Base
import src.app.models  # noqa: F401 – register all models with Base.metadata
from src.app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Werkzeugverwaltungstool API", version="0.1.0", lifespan=lifespan)

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