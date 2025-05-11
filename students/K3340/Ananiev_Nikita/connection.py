from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import URL

url_object = URL.create(
    "postgresql",
    username="postgres",
    password="aventador",
    host="localhost",
    database="book_share_db",
)

engine = create_engine(url_object, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session