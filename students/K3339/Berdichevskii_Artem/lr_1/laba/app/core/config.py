from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Hackathon project")

    DB_USER: str = os.getenv("POSTGRES_USER")
    DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    DB_HOST: str = os.getenv("POSTGRES_HOST")
    DB_PORT: str = os.getenv("POSTGRES_PORT")
    DB_NAME: str = os.getenv("POSTGRES_DB")

    DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True


settings = Settings()