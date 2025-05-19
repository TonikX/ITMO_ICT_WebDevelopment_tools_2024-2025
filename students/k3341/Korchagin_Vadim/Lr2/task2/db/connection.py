import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession


load_dotenv()

db_url = os.getenv("DB_ADMIN") 
engine: AsyncEngine = create_async_engine(db_url, echo=False, future=True)

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_async_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session