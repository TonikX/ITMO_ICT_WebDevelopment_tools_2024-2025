import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_DSN = os.getenv("DB_URL")
JWT_SECRET=os.getenv("JWT_SECRET")