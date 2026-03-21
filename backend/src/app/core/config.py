# ============================================================
# config.py – Zentrale Konfiguration der Anwendung
#
# Alle Konfigurationswerte werden aus der .env-Datei gelesen.
# Pydantic Settings validiert automatisch, ob alle Pflichtfelder gesetzt sind.
# ============================================================

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pfad zur SQLite-Datenbankdatei (z.B. "sqlite:///./src/app/db/app.db")
    DATABASE_URL: str

    # JWT-Konfiguration – alle Werte kommen aus .env
    JWT_SECRET_KEY: str              # Geheimer Schlüssel zum Signieren der Tokens
    JWT_ALGORITHM: str               # Algorithmus (normalerweise "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int # Wie lange ein Token gültig ist (z.B. 60 Minuten)

    # Startwerte für den ersten Admin-Benutzer – werden beim ersten Start in die DB eingetragen
    SEED_MANAGER_EMAIL: str
    SEED_MANAGER_PASSWORD: str
    SEED_MANAGER_FIRSTNAME: str
    SEED_MANAGER_LASTNAME: str

    # Lädt die Werte aus backend/.env, wenn die App aus dem backend/-Ordner gestartet wird
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Globale Instanz – wird überall im Projekt importiert
settings = Settings()
