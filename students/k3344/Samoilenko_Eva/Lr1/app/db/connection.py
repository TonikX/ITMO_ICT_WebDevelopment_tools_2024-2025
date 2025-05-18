from pathlib import Path

from sqlmodel import SQLModel, Session, create_engine
import os
from dotenv import load_dotenv

# load_dotenv()
load_dotenv(Path("C:/Users/evasa/ITMO_ICT_WebDevelopment_tools_2024-2025/students/k3344"
                 "/Samoilenko_Eva/Lr1") / '.env')
db_url = os.getenv('DB_ADMIN')
if not db_url:
    raise ValueError("Не найдена переменная DB_ADMIN в .env файле")
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
