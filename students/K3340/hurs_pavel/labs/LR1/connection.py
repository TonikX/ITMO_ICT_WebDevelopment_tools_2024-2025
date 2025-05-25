import os
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:password@localhost/time_manager_db")

engine = create_engine(DATABASE_URL)

# Указываем класс сессии как Session из SQLModel и отключаем автоматическое истечение срока действия объектов
SessionLocal = sessionmaker(
    bind=engine, 
    class_=Session, 
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)
