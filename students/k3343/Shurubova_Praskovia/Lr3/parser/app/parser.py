from fastapi import HTTPException
import aiohttp
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import Optional
from .model import RealBook
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_ADMIN")
async_engine = create_async_engine(DB_URL.replace("postgresql://", "postgresql+asyncpg://"))
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        if response.status != 200:
            raise HTTPException(status_code=response.status, detail="Ошибка при загрузке страницы")
        return await response.text()


def parse_book_item(book_item) -> Optional[dict]:
    try:
        title_elem = book_item.find('a', class_='book-item__title')
        if not title_elem:
            return None
        title = title_elem.text.strip()

        author_elem = book_item.find('a', class_='book-item__author')
        if not author_elem:
            return None
        author = author_elem.text.strip()

        edition_table = book_item.find('table', class_='book-item-edition')
        year = None
        publisher = None

        if edition_table:
            year_row = edition_table.find('td', string='Год издания:')
            if year_row:
                year_td = year_row.find_next_sibling('td')
                if year_td:
                    year_str = year_td.text.strip()
                    if year_str.isdigit():
                        year = int(year_str)

            publisher_row = edition_table.find('td', string='Издательство:')
            if publisher_row:
                publisher_td = publisher_row.find_next_sibling('td')
                if publisher_td:
                    publisher_link = publisher_td.find('a', class_='lists-edition__link')
                    publisher = publisher_link.text.strip() if publisher_link else publisher_td.text.strip().split(',')[0].strip()

        description_div = book_item.find('div', class_='book-item-desc')
        description = description_div.find('p').text.strip() if description_div and description_div.find('p') else "Описание недоступно"

        if not all([title, author, year, publisher]):
            return None

        return {
            "name": title,
            "author": author,
            "year": year,
            "publisher": publisher,
            "description": description
        }

    except Exception:
        return None



async def parse_genre_page(url: str):
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, 'html.parser')

        books = []

        for book_item in soup.find_all('div', class_='book-item__inner'):
            book_data = parse_book_item(book_item)
            if book_data:
                books.append(book_data)

        return books



async def save_books_to_db(books: list[dict]):
    async with AsyncSessionLocal() as session:
        for book in books:
            db_book = RealBook(**book)
            session.add(db_book)
        await session.commit()
    return len(books)


async def parse_and_save_book(url: str):
    try:
        books = await parse_genre_page(url)
        count = await save_books_to_db(books)
        return count
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data processing error: {str(e)}")