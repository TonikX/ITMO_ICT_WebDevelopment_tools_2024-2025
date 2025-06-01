import os
import time
from sqlite3 import OperationalError

from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
load_dotenv()

db_url = os.getenv('DB_TIME')

if not db_url:
    raise ValueError("DB_TIME environment variable is not set")

engine = create_engine(db_url, echo=True)


def init_db():
    retries = 5
    while retries > 0:
        try:
            SQLModel.metadata.create_all(engine)
            break
        except OperationalError:
            retries -= 1
            time.sleep(2)

def get_session():
    with Session(engine) as session:
        yield session