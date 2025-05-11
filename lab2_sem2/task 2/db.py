from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


def get_session() -> Session:
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


def init_db():
    SQLModel.metadata.create_all(engine)

