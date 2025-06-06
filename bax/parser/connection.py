from sqlmodel import SQLModel, Session, create_engine

from dotenv import load_dotenv

load_dotenv()

db_url = 'postgresql://postgres:postgres@db:5432/postgres'
#db_url = 'postgresql://postgres:postgres@localhost:5432/postgres'
engine = create_engine(db_url, echo=False)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session