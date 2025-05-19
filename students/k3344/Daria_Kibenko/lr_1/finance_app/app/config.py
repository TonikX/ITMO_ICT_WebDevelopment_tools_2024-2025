import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "9379")
DB_USER = os.getenv("DB_USER", "finance_user")
DB_PASS = os.getenv("DB_PASS", "finance_pass")
DB_NAME = os.getenv("DB_NAME", "finance_db")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
