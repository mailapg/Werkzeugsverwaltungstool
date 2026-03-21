# ============================================================
# session.py – Datenbankverbindung und Session-Factory
#
# Aufgaben:
#   1. SQLAlchemy-Engine erstellen (Verbindung zur Datenbank)
#   2. SQLite-Fremdschlüssel-Constraints aktivieren (standardmäßig aus)
#   3. SessionLocal-Factory für Datenbankoperationen bereitstellen
# ============================================================

import sqlite3
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.app.core.config import settings


def _ensure_sqlite_dir_exists(db_url: str) -> None:
    """Stellt sicher, dass der Ordner für die SQLite-Datenbankdatei existiert."""
    if db_url.startswith("sqlite:///"):
        rel_path = db_url.replace("sqlite:///", "", 1)  # z.B. ./src/app/db/app.db
        p = Path(rel_path)
        if not p.is_absolute():
            p.parent.mkdir(parents=True, exist_ok=True)


# Ordner anlegen bevor die Engine erstellt wird
_ensure_sqlite_dir_exists(settings.DATABASE_URL)

# check_same_thread=False: Erlaubt mehrere Threads auf dieselbe SQLite-Verbindung zuzugreifen.
# FastAPI nutzt mehrere Threads – ohne diese Option würde SQLite Fehler werfen.
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

# SQLAlchemy-Engine erstellen (verwaltet den Verbindungspool zur Datenbank)
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_fk_pragma(dbapi_connection, _connection_record):
        """
        Aktiviert Fremdschlüssel-Constraints für SQLite.

        WICHTIG: SQLite hat Fremdschlüssel standardmäßig DEAKTIVIERT.
        Ohne dieses PRAGMA könnte man z.B. einen Benutzer löschen,
        obwohl er noch aktive Ausleihen hat – ohne Fehlermeldung.
        Dieses Event wird bei JEDER neuen Datenbankverbindung ausgeführt.
        """
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

# Session-Factory: Jede Datenbankoperation bekommt eine eigene Session.
# autocommit=False: Änderungen müssen explizit mit db.commit() gespeichert werden.
# autoflush=False:  SQLAlchemy sendet SQL erst bei commit(), nicht schon früher.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)