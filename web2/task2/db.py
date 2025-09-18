from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
import os

os.environ["ASYNC_DB_URL"] = "postgresql+asyncpg://postgres:12345@localhost/laba2web"
os.environ["DB_URL"] = "postgresql://postgres:12345@localhost/laba2web"


db_url = os.environ["DB_URL"]
async_db_url = os.environ["ASYNC_DB_URL"]


engine = create_engine(db_url, echo=True)
SessionLocal = sessionmaker(bind=engine)
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
