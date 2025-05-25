from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker
from .config import settings
from models.base import Base

def create_db_url() -> engine.URL:
    return engine.url.URL.create(
        drivername='postgresql+psycopg2',
        database=settings.POSTGRES_DB,
        username=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
    )

db_engine = create_engine(create_db_url())

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
