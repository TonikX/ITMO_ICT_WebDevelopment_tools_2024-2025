from celery import Celery
from base import parse_books_from_genre_page
from connection import create_tables, get_session
from models import Book, UserBook
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Celery('parser', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

async def save_books_to_db(books, user_id=1):
    logger.debug(f"Saving {len(books)} books to database")
    async for session in get_session():
        for book_data in books:
            try:
                stmt = select(Book).where(
                    (Book.isbn == book_data["isbn"]) |
                    ((Book.title == book_data["title"]) & (Book.author == book_data["author"]))
                )
                result = await session.execute(stmt)
                existing_book = result.scalar_one_or_none()

                if not existing_book:
                    book = Book(**book_data)
                    session.add(book)
                    await session.flush()
                    book_id = book.book_id
                    logger.debug(f"Added new book: {book.title}, ID: {book_id}")
                else:
                    book_id = existing_book.book_id
                    logger.debug(f"Book already exists: {existing_book.title}, ID: {book_id}")

                stmt = select(UserBook).where(
                    (UserBook.user_id == user_id) & (UserBook.book_id == book_id)
                )
                result = await session.execute(stmt)
                existing_user_book = result.scalar_one_or_none()

                if not existing_user_book:
                    user_book = UserBook(
                        user_id=user_id,
                        book_id=book_id,
                        status="available",
                        location="unknown"
                    )
                    session.add(user_book)
                    logger.debug(f"Added UserBook for user_id: {user_id}, book_id: {book_id}")
                else:
                    logger.debug(f"UserBook already exists for user_id: {user_id}, book_id: {book_id}")

            except Exception as e:
                logger.error(f"Error saving book {book_data.get('title')}: {e}")
                continue

async def run_parse_and_save(url, genre, user_id):
    logger.debug(f"Starting task for URL: {url}, genre: {genre}")
    books = await parse_books_from_genre_page(url, genre, max_books=3)
    logger.debug(f"Parsed {len(books)} books")

    try:
        await create_tables()
        logger.debug("Ensured tables exist before saving")
    except Exception as e:
        logger.error(f"Error ensuring tables: {e}")
        raise

    if books:
        await save_books_to_db(books, user_id)
    else:
        logger.warning("No books parsed, skipping database save")

    return {"genre": genre, "books_saved": len(books)}

@app.task
def parse_and_save_task(url, genre, user_id=1):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(run_parse_and_save(url, genre, user_id))