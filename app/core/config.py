from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str
    DATABASE_URL: str
    ALLOWED_ORIGINS: List[str] 
    SECRET_KEY: str
    ALGORITHM: str
    TOKEN_EXPIRES_MINUTES: int

    class Config:
        env_file = ".env"

settings = Settings()
