import sqlite3
from pathlib import Path

from sqlalchemy import create_engine, event
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

if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_fk_pragma(dbapi_connection, _connection_record):
        """Aktiviert FK-Constraints für SQLite (standardmäßig deaktiviert)."""
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)