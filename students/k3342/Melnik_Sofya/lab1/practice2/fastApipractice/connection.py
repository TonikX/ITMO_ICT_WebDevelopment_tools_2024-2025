from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
import os
from sqlmodel import create_engine

load_dotenv()
db_url = os.getenv("DB_ADMIN")
engine = create_engine(db_url, echo=True)
# db_url = 'postgresql://postgres:123456@localhost/warriors_db'
# engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session