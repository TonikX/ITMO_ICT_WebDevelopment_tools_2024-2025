import os
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

# Загрузка переменных окружения из .env
load_dotenv()

# Получение URL базы данных из переменных окружения
DATABASE_URL = os.getenv("DB_ADMIN")
if not DATABASE_URL:
    raise RuntimeError("Environment variable DB_ADMIN is not set")

# Создание движка SQLAlchemy через SQLModel
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    """
    Инициализирует базу данных, создавая все таблицы
    """
    SQLModel.metadata.create_all(engine)

@contextmanager
def _session_manager() -> Generator[Session, None, None]:
    """
    Создание сессии с последующим закрытием после её завершения
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

def get_session():
    """
    Зависимость FastAPI для получения сессии к базе данных
    """
    from sqlmodel import Session
    with Session(engine) as session:
        yield session