from sqlmodel import SQLModel, Session, create_engine
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем URL из .env
DATABASE_URL = os.getenv("DB_ADMIN")

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session