import os
from sqlmodel import Session, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC")

engine_sync = create_engine(DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(
    bind=engine_sync,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)

def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

engine_async = create_async_engine(DATABASE_URL_ASYNC, echo=True, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine_async,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

async def get_async_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
