from sqlmodel import SQLModel, Session, create_engine
import os
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()
db_url = os.getenv('DB_ADMIN')
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
