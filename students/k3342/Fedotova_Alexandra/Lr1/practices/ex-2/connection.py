from sqlmodel import SQLModel, Session, create_engine
from models.models import *
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DB_ADMIN')
engine = create_engine(db_url, echo=True)

def init_db():
    try:
        print("Creating tables...")
        SQLModel.metadata.create_all(engine)
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

def get_session():
    with Session(engine) as session:
        yield session
