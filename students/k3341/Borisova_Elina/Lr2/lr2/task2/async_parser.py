import asyncio
import time
import aiohttp
import ssl
import certifi
from bs4 import BeautifulSoup
from sqlmodel import Session, SQLModel
from connection import engine
from lr2.task2.urls import urls
from models import Page

async def parse_and_save(url, session):
    try:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"HTTP Error {response.status} for {url}")
                return

            html = await response.text()
            bs = BeautifulSoup(html, "html.parser")

            title = None
            if bs.title and bs.title.string:
                title = bs.title.string.strip()
            elif bs.find("h1"):
                title = bs.find("h1").text.strip()

            with Session(engine) as db:
                page = Page(url=url, title=title)
                db.add(page)
                db.commit()
                print(f"Success: {url} | Title: {title if title else 'No title found'}")

    except Exception as e:
        print(f"Error parsing {url}: {str(e)}")

async def main():
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(
        ssl=ssl_context,
        limit=10,
        force_close=True,
        enable_cleanup_closed=True
    )

    start = time.time()

    async with aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=15)
    ) as session:
        tasks = [parse_and_save(url, session) for url in urls]
        await asyncio.gather(*tasks)

    end = time.time()
    print(f"\nAsync time: {end - start:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())