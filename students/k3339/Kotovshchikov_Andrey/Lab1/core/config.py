from typing import Annotated
from pydantic import Field, PositiveInt, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", extra="ignore")

    DATABASE_URI: PostgresDsn
    JWT_TTL: Annotated[PositiveInt, Field(default=60 * 60 * 3)]
    JWT_SECRET: str


settings = Settings()
