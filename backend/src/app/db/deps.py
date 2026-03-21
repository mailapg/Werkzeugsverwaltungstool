# ============================================================
# db/deps.py – FastAPI-Dependency für Datenbankverbindungen
#
# get_db() wird als Dependency in allen Endpunkten verwendet, die
# Datenbankzugriff brauchen. FastAPI kümmert sich darum, dass die Session
# nach der Anfrage automatisch geschlossen wird – auch bei Fehlern.
# ============================================================

from typing import Generator
from src.app.db.session import SessionLocal


def get_db() -> Generator:
    """
    Stellt eine Datenbankverbindung für einen API-Endpunkt bereit.

    Verwendung in einem Endpunkt:
        @router.get("/users")
        def get_users(db: Session = Depends(get_db)):
            ...

    Das 'yield' macht dies zu einem Kontext-Manager:
      - Vor 'yield': Session öffnen
      - Nach 'yield' (auch bei Ausnahmen): Session schließen
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()