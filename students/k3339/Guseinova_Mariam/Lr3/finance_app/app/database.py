from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from common.models.base import Base

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)