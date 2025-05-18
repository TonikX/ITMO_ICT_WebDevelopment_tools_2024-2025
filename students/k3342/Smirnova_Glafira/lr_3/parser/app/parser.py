import aiohttp
import asyncpg
from bs4 import BeautifulSoup
from typing import Optional
from sqlmodel import SQLModel, Field
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL")

class BookParsed(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    author: str = Field(index=True)
    year: int
    publisher: str

async def async_parse(url: str) -> int:
    count = 0
    conn = await asyncpg.connect(DB_URL)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS bookparsed (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            author TEXT NOT NULL,
            year INTEGER NOT NULL,
            publisher TEXT NOT NULL
        )
    ''')
    await conn.close()

    async def parse_genre_page(url: str, session: aiohttp.ClientSession, pool: asyncpg.Pool):
        nonlocal count
        try:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                books_data = []
                for book_item in soup.find_all('div', class_='book-item__inner'):
                    book = parse_book(book_item)
                    if book:
                        books_data.append((book.name, book.author, book.year, book.publisher))

                if books_data:
                    async with pool.acquire() as conn:
                        await conn.executemany('''
                            INSERT INTO bookparsed (name, author, year, publisher)
                            VALUES ($1, $2, $3, $4)
                        ''', books_data)
                    count += len(books_data)

        except Exception as e:
            pass

    pool = await asyncpg.create_pool(DB_URL)

    async with aiohttp.ClientSession() as session:
        await parse_genre_page(url, session, pool)

    await pool.close()
    return count


def parse_book(book_item) -> Optional[BookParsed]:
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
                    if publisher_link:
                        publisher = publisher_link.text.strip()
                    else:
                        publisher = publisher_td.text.strip().split(',')[0].strip()

        if not all([title, author, year, publisher]):
            return None

        return BookParsed(name=title, author=author, year=year, publisher=publisher)

    except Exception:
        return None