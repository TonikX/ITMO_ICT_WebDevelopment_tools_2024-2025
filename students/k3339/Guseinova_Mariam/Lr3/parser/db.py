from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from common.models.base import Base

load_dotenv()

# Синхронное подключение
sync_engine = create_engine(os.getenv("SYNC_DB_URL"))
SyncSession = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Асинхронное подключение
async_engine = create_async_engine(os.getenv("ASYNC_DB_URL"))
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

def init_sync_db():
    # Создаем только таблицу пользователей
    Base.metadata.tables["user"].create(bind=sync_engine, checkfirst=True)
    # Base.metadata.create_all(bind=sync_engine)

async def init_async_db():
    async with async_engine.begin() as conn:
        # Создаем только таблицу пользователей
        await conn.run_sync(
            lambda sync_conn: Base.metadata.tables["user"].create(
                bind=sync_conn, checkfirst=True
            )
        )
        # await conn.run_sync(Base.metadata.create_all)