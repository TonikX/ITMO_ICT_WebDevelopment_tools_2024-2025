import os
import logging
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlmodel import SQLModel
from models import Book, User, UserBook
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Retry configuration for connection check
@retry(
    stop=stop_after_attempt(10),  # Increased retries
    wait=wait_exponential(multiplier=1, min=2, max=15),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: logger.debug(
        f"Retrying ({retry_state.attempt_number}/10) after {retry_state.idle_for}s due to {retry_state.outcome.exception()}"
    )
)
async def check_db_connection(engine):
    logger.debug("Checking database connection")
    async with AsyncSession(engine, expire_on_commit=False) as session:
        await session.execute(text("SELECT 1"))
    logger.debug("Database connection successful")

async def create_tables():
    # Load environment variables
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        logger.error("DATABASE_URL is not set in environment variables")
        raise ValueError("DATABASE_URL is not set")

    logger.debug(f"Using DATABASE_URL: {DATABASE_URL}")

    # Create async engine with increased timeout
    try:
        engine = create_async_engine(
            DATABASE_URL,
            echo=True,
            connect_args={"timeout": 30}  # Increased connection timeout
        )
        logger.debug("Database engine created successfully")
    except Exception as e:
        logger.error(f"Failed to create engine: {e}")
        raise

    # Initial wait to ensure DB is ready
    logger.debug("Waiting for database to be ready")
    await asyncio.sleep(5)  # Wait 5 seconds initially

    # Check database connection
    try:
        await check_db_connection(engine)
    except Exception as e:
        logger.error(f"Database not ready: {e}")
        raise

    # Create tables
    logger.debug("Starting table creation")
    try:
        async with engine.begin() as conn:
            # await conn.run_sync(SQLModel.metadata.drop_all)  # Uncomment to drop tables first
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.debug("Tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise
    finally:
        await engine.dispose()
        logger.debug("Database engine disposed")

if __name__ == "__main__":
    asyncio.run(create_tables())