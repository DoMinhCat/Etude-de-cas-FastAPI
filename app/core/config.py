from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()
class Settings(BaseSettings):
    APP_NAME: str | None = os.getenv("APP_NAME")
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")
    ALLOWED_ORIGINS: str | None = os.getenv("ALLOWED_ORIGINS")
    SECRET_KEY: str | None = os.getenv("SECRET_KEY")
    ALGORITHM: str | None = os.getenv("ALGORITHM")
    TOKEN_EXPIRES_MINUTES: int = int(os.getenv("TOKEN_EXPIRES_MINUTES", "30"))

    POSTGRES_HOST: str | None = os.getenv("POSTGRES_HOST")
    POSTGRES_USER: str | None = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str | None= os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str | None = os.getenv("POSTGRES_DB")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))

    class Config:
        env_file = ".env"

settings = Settings()

