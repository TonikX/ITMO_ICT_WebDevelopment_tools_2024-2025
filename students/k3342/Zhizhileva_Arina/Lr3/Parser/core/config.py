from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key"  # Замените на безопасный ключ
    ALGORITHM: str = "HS256"

settings = Settings()