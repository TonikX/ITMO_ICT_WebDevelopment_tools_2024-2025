import asyncio
import aiohttp
import psycopg2
from bs4 import BeautifulSoup
import time


def create_aiohttp_session():
    return aiohttp.ClientSession()


async def parse_and_save(url, session):
    async with session.get(url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string

        conn = psycopg2.connect("dbname=finance_db user=postgres password=12345678 host=localhost")
        cur = conn.cursor()

        cur.execute("INSERT INTO async (url, title) VALUES (%s, %s)", (url, title))
        conn.commit()

        print(f"Заголовок {url}: {title}")

        cur.close()
        conn.close()


async def main():
    urls = ["https://ostrovok.ru/", "https://www.avito.ru/", "https://www.cian.ru/"]
    tasks = []

    async with create_aiohttp_session() as session:
        for url in urls:
            task = asyncio.create_task(parse_and_save(url, session))
            tasks.append(task)

        await asyncio.gather(*tasks)


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Время выполнения: {execution_time} секунд(ы)")