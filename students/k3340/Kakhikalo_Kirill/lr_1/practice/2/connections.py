from sqlmodel import SQLModel, Session, create_engine
from model import Base

from sqlalchemy import URL

db_url = URL.create(
    "postgresql+pg8000",
    username="postgres",
    password="12345678",
    host="127.0.0.1",
    port=5432,
    database="appdb",
)

engine = create_engine(db_url, echo=True)


def init_db():
    Base.metadata.create_all(engine)
    print('created tables')


def get_session():
    with Session(engine) as session:
        yield session