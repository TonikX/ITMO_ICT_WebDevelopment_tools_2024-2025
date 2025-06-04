import time
import aiohttp
import asyncio
from bs4 import BeautifulSoup

from config import *
from models import *
from connection import *


async def fetch(session, url):
    async with session.get(url) as response:
        return url, await response.text()


async def parse_and_save(session, url):
    url, html = await fetch(session, url)
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title else "No title"

    with get_session() as session:
        page = Page(url=url, title=title)
        session.merge(page)
        session.commit()


async def main():
    init_db()

    start = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, url) for url in URLS]
        await asyncio.gather(*tasks)

    print(f"Время: {time.time() - start:.2f} сек")


if __name__ == "__main__":
    asyncio.run(main())
