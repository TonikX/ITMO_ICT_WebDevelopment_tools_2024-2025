from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Default DATABASE_URL for Docker
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/book_exchange")
if not DATABASE_URL:
    logger.error("DATABASE_URL is not set in environment variables")
    raise ValueError("DATABASE_URL is not set")

logger.debug(f"Using DATABASE_URL: {DATABASE_URL}")

try:
    engine = create_async_engine(DATABASE_URL, echo=True, future=True)
except Exception as e:
    logger.error(f"Failed to create engine: {e}")
    raise

async def create_tables():
    logger.debug("Checking and creating tables if necessary")
    try:
        async with engine.begin() as conn:
            # Check if tables exist to avoid redundant creation
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.debug("Tables ensured successfully")
    except Exception as e:
        logger.error(f"Error ensuring tables: {e}")
        raise

async def get_session():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()