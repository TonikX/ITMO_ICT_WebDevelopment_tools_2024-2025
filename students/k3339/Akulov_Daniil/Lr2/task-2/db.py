from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()

db_url = os.getenv('LAB1_DB_URL')
async_db_url = os.getenv('LAB1_ASYNC_DB_URL')


engine = create_engine(db_url, echo=True)
SessionLocal = sessionmaker(bind=engine)


async_engine = create_async_engine(async_db_url, echo=False)
AsyncSessionLocal = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


def init_db():
    SQLModel.metadata.create_all(engine)


async def async_init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
