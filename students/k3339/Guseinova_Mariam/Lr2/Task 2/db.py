from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Синхронные подключения
sync_engine = create_engine(os.getenv("SYNC_DB_URL"))
SyncSession = sessionmaker(bind=sync_engine)

# Асинхронные подключения
async_engine = create_async_engine(os.getenv("ASYNC_DB_URL"))
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

def init_sync_db():
    SQLModel.metadata.create_all(sync_engine)

async def init_async_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)