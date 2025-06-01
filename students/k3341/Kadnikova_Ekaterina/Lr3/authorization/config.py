import os

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "richardrichardrichard")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

settings = Settings()