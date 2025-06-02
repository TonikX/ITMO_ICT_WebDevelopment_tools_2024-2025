import os
from datetime import timedelta

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE: timedelta = timedelta(minutes=30)

    class Config:
        env_file = ".env"


settings = Settings()


print(settings.DATABASE_URL)


