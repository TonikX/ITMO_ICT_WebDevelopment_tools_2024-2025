from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from base import parse_books_from_genre_page
from connection import engine, create_tables
from models import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from celery_config import parse_and_save_task
import asyncio
from api.books import router as books_router
from api.users import router as users_router
from api.auth import router as auth_router
from api.exchanges import router as exchanges_router
from api.user_books import router as user_books_router
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Book Exchange API",
    description="API for managing a book exchange platform with user authentication, book management, and exchange requests.",
    version="1.0.0"
)

app.include_router(books_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(exchanges_router)
app.include_router(user_books_router)

@app.on_event("startup")
async def on_startup():
    await create_tables()

class ParseRequest(BaseModel):
    url: str
    genre: str
    user_id: int = 1

@app.post("/parse/sync")
async def parse_sync(request: ParseRequest):
    try:
        if "/tag/" in request.url:
            logger.warning(f"Parsing tag page: {request.url}. Expected genre page.")
        books = await parse_books_from_genre_page(request.url, request.genre, max_books=3)

        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            for book_data in books:
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
                else:
                    book_id = existing_book.book_id

                stmt = select(UserBook).where(
                    (UserBook.user_id == request.user_id) & (UserBook.book_id == book_id)
                )
                result = await session.execute(stmt)
                existing_user_book = result.scalar_one_or_none()

                if not existing_user_book:
                    user_book = UserBook(
                        user_id=request.user_id,
                        book_id=book_id,
                        status="available",
                        location="unknown"
                    )
                    session.add(user_book)

            await session.commit()

        return {"genre": request.genre, "books_saved": len(books), "books": books}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга: {str(e)}")

@app.post("/parse/async")
async def parse_async(request: ParseRequest):
    try:
        if "/tag/" in request.url:
            logger.warning(f"Queuing tag page: {request.url}. Expected genre page.")
        task = parse_and_save_task.delay(request.url, request.genre, request.user_id)
        return {"task_id": task.id, "status": "Задача поставлена в очередь"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка постановки задачи: {str(e)}")