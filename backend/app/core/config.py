# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    LOCAL_STORAGE_PATH: str = "./data/uploads"

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    GEMINI_API_KEY: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
