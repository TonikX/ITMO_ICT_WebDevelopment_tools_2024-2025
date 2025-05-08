from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from fastapi import Depends
from typing import Annotated
from config import DB_URL

engine = create_engine(
  DB_URL, # connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
  pass

def get_db():
  try:
    db = SessionLocal()
    yield db
  finally:
    db.close()

db_session = Annotated[Session, Depends(get_db)]