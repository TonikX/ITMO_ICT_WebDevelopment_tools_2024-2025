import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine

# загружаем .env из корня проекта
load_dotenv()

DATABASE_URL = os.getenv("DB_ADMIN")
if not DATABASE_URL:
    raise RuntimeError("Не задана переменная окружения DB_ADMIN")

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)
