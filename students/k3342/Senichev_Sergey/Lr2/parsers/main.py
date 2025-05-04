import asyncio
import logging
from sqlalchemy import create_engine
from .threading_parser import ThreadingParser
from .multiprocessing_parser import MultiprocessingParser
from .async_parser import AsyncParser
from .db_models import create_db_and_tables
from .config import DB_URL
from .summary import summary_logger
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    engine = create_engine(DB_URL)
    create_db_and_tables(engine)
    logger.info("Database and tables created successfully")

def run_threading_parser():
    logger.info("Starting threading parser...")
    parser = ThreadingParser()
    start_time = time.time()
    parser.run()
    end_time = time.time()
    summary_logger.add_parser_stats(
        "Threading Parser",
        start_time,
        end_time,
        len(parser.results),
        parser.errors if hasattr(parser, 'errors') else []
    )

def run_multiprocessing_parser():
    logger.info("Starting multiprocessing parser...")
    parser = MultiprocessingParser()
    start_time = time.time()
    parser.run()
    end_time = time.time()
    summary_logger.add_parser_stats(
        "Multiprocessing Parser",
        start_time,
        end_time,
        len(parser.results) if hasattr(parser, 'results') else 0,
        parser.errors if hasattr(parser, 'errors') else []
    )

async def run_async_parser():
    logger.info("Starting async parser...")
    parser = AsyncParser()
    start_time = time.time()
    await parser.run()
    end_time = time.time()
    summary_logger.add_parser_stats(
        "Async Parser",
        start_time,
        end_time,
        len(parser.results),
        parser.errors if hasattr(parser, 'errors') else []
    )

def main():
    # Create database and tables
    create_database()
    
    # Run threading parser
    run_threading_parser()
    
    # Run multiprocessing parser
    run_multiprocessing_parser()
    
    # Run async parser
    asyncio.run(run_async_parser())
    
    # Print summary
    summary_logger.print_summary()

if __name__ == "__main__":
    main() 