from sqlmodel import SQLModel, create_engine

DB_URL = "postgresql+psycopg2://postgres:89184890284p@localhost/bookcrossing_db"

engine = create_engine(DB_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)
    return engine
