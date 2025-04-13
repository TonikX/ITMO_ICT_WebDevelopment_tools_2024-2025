from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8
    DB_ADMIN: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()