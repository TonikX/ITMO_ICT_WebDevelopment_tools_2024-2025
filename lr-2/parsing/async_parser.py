import asyncio
import aiohttp
import asyncpg 
from bs4 import BeautifulSoup
import time

DB_CONFIG = {
    'host': 'localhost',
    'database': 'web_parsing',
    'user': 'postgres',
    'password': 'postgres'
}

async def parse_and_save(session, db_pool, url):
    """Асинхронная функция для парсинга и сохранения данных"""
    try:
        start_time = time.perf_counter()

        async with session.get(url, timeout=10) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.string if soup.title else 'No title'

        end_time = time.perf_counter()
        elapsed = end_time - start_time

        async with db_pool.acquire() as conn:
            await conn.execute(
                'INSERT INTO pages (url, title, execution_time, method) VALUES ($1, $2, $3, $4)',
                url, title, elapsed, "async"
            )

        print(f"Processed: {url} | Time: {elapsed:.2f}s | Method: async")

    except Exception as e:
        print(f"Failed to process {url}: {e}")

async def main():
    urls = [
        'https://my.itmo.ru',
        'https://www.github.com',
        'https://www.stackoverflow.com',
        'https://www.wikipedia.org',
        'https://www.youtube.com',
        'https://isu.ifmo.ru',
    ]

    db_pool = await asyncpg.create_pool(**DB_CONFIG)

    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, db_pool, url) for url in urls]
        await asyncio.gather(*tasks)

    await db_pool.close()
    print("Async parsing complete!")

if __name__ == "__main__":
    asyncio.run(main())
