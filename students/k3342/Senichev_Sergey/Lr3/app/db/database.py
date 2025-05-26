from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Annotated
from fastapi import Depends

from config import settings

engine = create_engine(settings.database.url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_database_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DatabaseSession = Annotated[Session, Depends(get_database_session)] 