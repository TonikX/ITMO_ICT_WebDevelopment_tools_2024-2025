from sqlmodel import Session, create_engine
from model import Base
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DB_ADMIN')

engine = create_engine(db_url, echo=True)


def init_db():
    Base.metadata.create_all(engine)
    print('created tables')


def get_session():
    with Session(engine) as session:
        yield session