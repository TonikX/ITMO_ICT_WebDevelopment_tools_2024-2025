from sqlmodel import SQLModel, Session, create_engine
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DB_ADMIN')

engine = create_engine(db_url, echo=True)


def init_db():
    try:
        SQLModel.metadata.create_all(engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise


def get_session():
    with Session(engine) as session:
        yield session