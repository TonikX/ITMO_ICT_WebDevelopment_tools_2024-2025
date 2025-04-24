import aiohttp
import asyncio
import time
from bs4 import BeautifulSoup
from sqlmodel import Session
from models import ParsedPage
from db import engine
from urls import urls


async def fetch(session, url):
    async with session.get(url) as response:
        html = await response.text()
        return url, html


async def parse_and_save(url, html):
    soup = BeautifulSoup(html, "lxml")
    title = soup.title.string if soup.title else "No title"
    with Session(engine) as session:
        page = ParsedPage(url=url, title=title)
        session.add(page)
        session.commit()
    print(f"[Async] Parsed: {url} — {title}")


async def main():
    from db import init_db
    init_db()
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        pages = await asyncio.gather(*tasks)

        parse_tasks = [parse_and_save(url, html) for url, html in pages]
        await asyncio.gather(*parse_tasks)
    print("Async Done in", time.time() - start, "seconds")


if __name__ == "__main__":
    asyncio.run(main())
