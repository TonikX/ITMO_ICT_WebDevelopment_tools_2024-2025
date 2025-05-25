from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = ""

    APP_PORT: int = 8000

    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str

    PARSER_PORT: int = 8080
    PARSER_HOST: str = "localhost"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"

    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"


settings = Settings()
