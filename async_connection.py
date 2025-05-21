import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

load_dotenv()
username = os.getenv("DB_USERNAME", "postgres")
password = os.getenv("DB_PASSWORD", "")
host = os.getenv("DB_HOST", "localhost")
database = os.getenv("DB_NAME", "web_team_finder")

async_db_url = f'postgresql+asyncpg://{username}:{password}@{host}/{database}'

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