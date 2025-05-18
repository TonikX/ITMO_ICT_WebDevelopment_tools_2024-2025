from fastapi import HTTPException
import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from .models import BookParsed
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL")
async_engine = create_async_engine(DB_URL.replace("postgresql://", "postgresql+asyncpg://"))


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail="Ошибка при загрузке страницы")
        return await response.text()


async def parse_books(url: str):
    """Парсинг книг автора с LiveLib"""
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, 'html.parser')

        author_element = soup.find('div', class_='author-header__name')
        if not author_element:
            raise HTTPException(status_code=400, detail="Не удалось найти автора на странице")

        author = author_element.text.strip()
        books = []

        for book_item in soup.find_all('div', class_='book-item__inner'):
            title_element = book_item.find('a', class_='book-item__title')
            if not title_element:
                continue

            title = title_element.text.strip()
            description = book_item.find('p')
            description = ".".join(
                description.text.strip().split(".")[:3]) + "." if description else None
            books.append({"author": author,
                          "title": title,
                          "description": description})

        return books


async def save_books(books):
    async with AsyncSession(async_engine) as connection:
        count = len(books)
        for book in books:
            db_book = BookParsed(**book)
            connection.add(db_book)

        await connection.commit()
    return count


async def parse_and_save_books(url):
    try:
        books = await parse_books(url)
        count = await save_books(books)
        return count
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Data processing error: {str(e)}"
        )
