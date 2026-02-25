from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    # JWT – Werte kommen aus .env
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Initialer Seed-Benutzer (Abteilungsleiter) – Werte kommen aus .env
    SEED_MANAGER_EMAIL: str
    SEED_MANAGER_PASSWORD: str
    SEED_MANAGER_FIRSTNAME: str
    SEED_MANAGER_LASTNAME: str

    # lädt backend/.env wenn du aus backend/ startest
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
