from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.core.config import settings


def _ensure_sqlite_dir_exists(db_url: str) -> None:
    if db_url.startswith("sqlite:///"):
        rel_path = db_url.replace("sqlite:///", "", 1)  # ./src/app/db/app.db
        p = Path(rel_path)
        if not p.is_absolute():
            p.parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_dir_exists(settings.DATABASE_URL)

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)