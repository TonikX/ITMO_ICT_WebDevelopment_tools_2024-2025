import asyncio
import aiohttp
import asyncpg
from bs4 import BeautifulSoup
import time


def create_aiohttp_session():
    return aiohttp.ClientSession()


async def parse_and_save(url, session, db_pool):
    async with session.get(url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else 'No title'

        async with db_pool.acquire() as connection:
            await connection.execute(
                "INSERT INTO async (url, title) VALUES ($1, $2)", url, title
            )

        print(f"Заголовок {url}: {title}")


async def main():
    urls = ["https://ostrovok.ru/", "https://www.avito.ru/", "https://www.cian.ru/"]

    db_pool = await asyncpg.create_pool(
        user='postgres',
        password='12345678',
        database='finance_db',
        host='localhost'
    )

    tasks = []

    async with create_aiohttp_session() as session:
        for url in urls:
            task = asyncio.create_task(parse_and_save(url, session, db_pool))
            tasks.append(task)

        await asyncio.gather(*tasks)

    await db_pool.close()


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time:.2f} секунд(ы)")
