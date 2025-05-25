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


    class Config:
        env_file = "../.env"


settings = Settings()
