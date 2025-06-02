import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()

db_password = os.environ["DB_PASSWORD"]
db_name = os.environ["DB_NAME"]
db_admin = os.environ["DB_ADMIN"]

db_url = f"postgresql://{db_admin}:{db_password}@db:5432/{db_name}"
engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
