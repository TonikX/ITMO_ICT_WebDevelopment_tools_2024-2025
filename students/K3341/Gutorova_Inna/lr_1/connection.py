import os

from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
load_dotenv()

db_url = os.getenv('DB_TIME')

if not db_url:
    raise ValueError("DB_TIME environment variable is not set")

engine = create_engine(db_url, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session