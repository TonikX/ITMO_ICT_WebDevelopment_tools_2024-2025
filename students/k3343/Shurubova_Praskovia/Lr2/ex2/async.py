import asyncio
import time
import aiohttp
import asyncpg
from parser import parse_genre_page
from model import RealBook

DB_URL = "postgresql://postgres:89184890284p@localhost/bookcrossing_db"

URLS = [
    "https://www.livelib.ru/genre/Современная-зарубежная-литература",
    "https://www.livelib.ru/genre/Книги-о-войне"
]


async def save_books_to_db(pool, books: list[RealBook]):
    async with pool.acquire() as conn:
        await conn.executemany('''
            INSERT INTO realbook (name, author, year, publisher, description)
            VALUES ($1, $2, $3, $4, $5)
        ''', [(b.name, b.author, b.year, b.publisher, b.description) for b in books])



async def parse_and_save(url, session, pool):
    try:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Не удалось загрузить страницу {url}, статус {response.status}")
                return

            html = await response.text()
            books = await asyncio.to_thread(parse_genre_page, html)

            valid_books = [b for b in books if b.name and b.author and b.year and b.publisher]

            if valid_books:
                await save_books_to_db(pool, valid_books)
                print(f"Сохранено {len(valid_books)} книг с {url}")
            else:
                print(f"Нет валидных книг на странице {url}")
    except Exception as e:
        print(f"Ошибка при обработке {url}: {e}")



async def main():
    start = time.perf_counter()
    pool = await asyncpg.create_pool(DB_URL)

    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(url, session, pool) for url in URLS]
        await asyncio.gather(*tasks)

    await pool.close()
    print(f"\nAsync выполнен за {time.perf_counter() - start:.2f} секунд.")


if __name__ == "__main__":
    asyncio.run(main())
