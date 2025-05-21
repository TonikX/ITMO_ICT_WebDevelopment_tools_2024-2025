import time
from bs4 import BeautifulSoup
import os
import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv

import aiohttp

n = 4
urls = [
    "https://www.litres.ru/popular/",
    "https://www.litres.ru/new/",
]

urls = urls + [f"https://www.litres.ru/{selection}/?page={page}" for selection in ["popular", "new"] for page in range(1, ((n - 2) // 2) + 1)]

async def parse(url: str):
    print(url)
    results = []
    load_dotenv()
    db_url = os.getenv('DB_ADMIN')
    engine = create_async_engine(db_url)
    AsyncSession = async_sessionmaker(bind=engine)

    async with aiohttp.ClientSession() as http_session:
        async with http_session.get(url) as response:
            soup = BeautifulSoup(await response.text(), features="html.parser")

            books = soup.find_all("div", { "class": "ArtInfo_info__BgoQR"} )

            for book in books:
                try:
                    title = book.find("a", { "data-testid": "art__title"}).text
                except:
                    title = None
                try:
                    author = book.find("a", { "data-testid": "art__authorName"}).text
                except:
                    author = None

                results.append((title, author))
                print("INSERT INTO book (title, author) VALUES (:title, :author)", {"title": title, "author": author}) 

            session = AsyncSession()
            result = await session.execute(text("SELECT * from public.book"))
            print(len(result.scalar()))   
    
            await session.close()

    await engine.dispose()

    return results

async def main(urls):
    start_time = time.perf_counter()

    tasks = []
    for url in urls:
        task = asyncio.create_task(parse(url))
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    results = [item for sublist in results for item in sublist]
    print(len(results))

    print(f"Время: {time.perf_counter() - start_time}")

if __name__ == "__main__":
    asyncio.run(main(urls))