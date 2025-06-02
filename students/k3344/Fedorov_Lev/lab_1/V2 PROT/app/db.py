import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import settings
from .models import Base

engine = None
AsyncSessionFactory = None
logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 2


async def setup_database(database_url: str):
    """Initialize database once at application startup"""
    global engine, AsyncSessionFactory

    logger.info("Setting up database connection...")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            engine = create_async_engine(
                database_url,
                echo=False,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_pre_ping=True,
            )

            AsyncSessionFactory = sessionmaker(
                engine, expire_on_commit=False, class_=AsyncSession
            )

            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            logger.info("Database connection established successfully")
            return AsyncSessionFactory

        except Exception as e:
            logger.error(f"Database connection failed (attempt {attempt}/{MAX_RETRIES}): {str(e)}")
            if attempt < MAX_RETRIES:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                await asyncio.sleep(RETRY_DELAY)
            else:
                logger.critical("Failed to connect to database after multiple attempts")
                raise

async def get_session():
    """Get a session for dependency injection"""
    global AsyncSessionFactory

    if AsyncSessionFactory is None:
        from .config import settings
        await setup_database(settings.database_url)

    async with AsyncSessionFactory() as session:
        yield session