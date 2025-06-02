from sqlalchemy import text
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from task2.database.models import Category, User
from sqlmodel import select

load_dotenv()

db_url = os.getenv('DB_ADMIN')
engine = create_async_engine(db_url, echo=True)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session():
    async with async_session() as session:
        yield session

async def close_db():
    await engine.dispose()

async def init_categories():
    async for session in get_session():
        await session.execute(text('DELETE FROM taskcategory'))
        await session.execute(text('DELETE FROM task'))
        for name in ["Answered", "Unanswered"]:
            existing = (await session.execute(select(Category).where(Category.name == name))).scalar_one_or_none()
            if not existing:
                session.add(Category(name=name))
        await session.commit()
        
async def init_users():
    async for session in get_session():
        existing = await session.execute(select(User).where(User.id == 1))
        if not existing.scalar_one_or_none():
            user = User(id=1, email='demo@example.com', name="name", hashed_password='...')
            session.add(user)
            await session.commit()