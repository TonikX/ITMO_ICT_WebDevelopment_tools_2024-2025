from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
import os

# Синхронный URL (для create_engine)
db_url = "postgresql://postgres:123@localhost/laba2web"
# Асинхронный URL (для create_async_engine)
async_db_url = "postgresql+asyncpg://postgres:123@localhost/laba2web"

# Синхронный движок
engine = create_engine(db_url, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Асинхронный движок
async_engine = create_async_engine(async_db_url, echo=True)
AsyncSessionLocal = sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)


def init_db():
    SQLModel.metadata.create_all(engine)


async def async_init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
