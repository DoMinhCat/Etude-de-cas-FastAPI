from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "GarageOS"
    # Par défaut: SQLite fichier (facile en local). Switchez vers Postgres via .env.
    DATABASE_URL: str = "sqlite:///./garageos.db"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
