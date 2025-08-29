from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()
class Settings(BaseSettings):
    APP_NAME: str = "GarageOS"
    DATABASE_URL: str = "postgresql+asyncpg://garage:garage_password@products_db:5432/GarageOS"
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    SECRET_KEY: str = "DEPLANO"
    ALGORITHM: str = "HS256"
    TOKEN_EXPIRES_MINUTES: int = 30
    POSTGRES_HOST: str = "products_db"
    POSTGRES_USER: str = "garage"
    POSTGRES_PASSWORD: str = "garage_password"
    POSTGRES_DATABASE: str = "GarageOS"
    POSTGRES_PORT: int = 5432

    class Config:
        env_file = ".env"

settings = Settings()

