import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

load_dotenv()

db_password = os.environ["DB_PASSWORD"]
db_name = os.environ["DB_NAME"]
db_admin = os.environ["DB_ADMIN"]

async_db_url = f"postgresql+asyncpg://{db_admin}:{db_password}@db:5432/{db_name}"

async_engine = create_async_engine(
    async_db_url,
    echo=True,
    future=True
)

# Создаем фабрику асинхронных сессий
async_session_factory = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_async_db():
    """Инициализирует асинхронную базу данных"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_async_session():
    """Возвращает асинхронную сессию базы данных"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_async_db():
    """Возвращает асинхронную сессию базы данных (альтернативный вариант)"""
    session = async_session_factory()
    try:
        yield session
    finally:
        await session.close()