# database.py
import os
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DB_TIME')

if not db_url:
    raise ValueError("DB_TIME environment variable is not set")

engine = create_engine(db_url, echo=True)
async_engine = create_async_engine(
    db_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=True
)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def get_async_session():
    return AsyncSessionLocal()
