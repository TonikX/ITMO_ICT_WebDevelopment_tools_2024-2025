import time

import asyncio
import aiohttp
import asyncpg
from bs4 import BeautifulSoup

from students.k3342.Smirnova_Glafira.lr_2.task2_parsing.db import DB_URL
from students.k3342.Smirnova_Glafira.lr_2.task2_parsing.logger import logger
from students.k3342.Smirnova_Glafira.lr_2.task2_parsing.parser import GENRE_URLS, parse_book


async def async_approach():
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
        try:
            logger.info(f"Парсинг страницы: {url}")
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
                        logger.info(f"Сохранено {len(books_data)} книг с {url}")

        except Exception as e:
            logger.error(f"Ошибка при парсинге {url}: {str(e)}")

    start_time = time.time()
    pool = await asyncpg.create_pool(DB_URL)

    async with aiohttp.ClientSession() as session:
        tasks = [parse_genre_page(url, session, pool) for url in GENRE_URLS]
        await asyncio.gather(*tasks)

    await pool.close()
    logger.info(f"Async завершён за {time.time() - start_time:.2f} сек")


if __name__ == "__main__":
    asyncio.run(async_approach())
