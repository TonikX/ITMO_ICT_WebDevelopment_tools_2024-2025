import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_DSN = os.getenv("DB_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
ITMO_LOGIN = os.getenv("ITMO_LOGIN")
ITMO_PASSWORD = os.getenv("ITMO_PASSWORD")
PARSER_URL = os.getenv("PARSER_URL", "http://localhost:8000/parse")
REDIS_DSN = os.getenv("REDIS_URL", "redis://localhost:6379/0")
