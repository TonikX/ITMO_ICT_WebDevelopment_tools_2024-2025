import asyncio
import time
import aiohttp
from bs4 import BeautifulSoup
from sqlmodel import Session

from connection import engine
from models import Page




async def parse_and_save(url, session):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                print(f"Ошибка {response.status} для {url}")
                return
            html = await response.text()
            bs = BeautifulSoup(html, "html.parser")
            title = bs.title.string if bs.title else bs.find("h1").text.strip() if bs.find("h1") else None
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {e}")
        return


    with Session(engine) as db:
        with db.begin():
            page = Page(url=url, title=title)
            db.add(page)
            db.flush()
            print(f"Парсинг завершён: {url} | Заголовок: {title}")


async def main(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(url, session) for url in urls]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    urls = [
        "https://example.com",
        "https://news.ycombinator.com",
        "https://github.com",
        "https://en.wikipedia.org/wiki/Hackathon",

        "https://www.python.org",
        "https://wikipedia.org/wiki/Hackathon",

        "https://www.kaggle.com/events",
        "https://techcrunch.com/startups/"
    ]

    start = time.time()
    asyncio.run(main(urls))
    end = time.time()
    print(f"\nВремя выполнения (async): {end - start:.2f} секунд")