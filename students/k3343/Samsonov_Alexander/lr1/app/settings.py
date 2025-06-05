from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_dsn: str = "postgresql+asyncpg://user:password@localhost/dbname"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
