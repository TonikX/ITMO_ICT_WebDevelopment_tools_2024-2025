import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Настройки для подключения к сервису парсеров
    PARSER_HOST: str = "localhost"
    PARSER_PORT: int = 8001

    # Настройки базы данных
    DATABASE_URL: str
    SYNC_DB_URL: str = ""
    ASYNC_DB_URL: str = ""

    # JWT настройки
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        extra = "ignore"  # Разрешаем дополнительные переменные


settings = Settings()

# Автоматическое определение Docker-окружения
if os.getenv("DOCKER_ENV") == "true":
    settings.PARSER_HOST = "parser"