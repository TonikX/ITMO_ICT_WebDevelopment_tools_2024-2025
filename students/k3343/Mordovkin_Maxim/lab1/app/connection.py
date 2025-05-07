import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine

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


def get_session():
    """
    Зависимость FastAPI для получения сессии к базе данных
    """
    from sqlmodel import Session
    with Session(engine) as session:
        yield session