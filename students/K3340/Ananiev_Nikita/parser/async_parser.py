import asyncio
import random

from aiohttp import ClientSession
from helpers import parse_book_links, parse_book_details
from database import BookInfoParsed
from typing import Optional

books_count = 100
workers_count = 4

async def get_books_links(urls) -> list[str]:
    links = []
    async with ClientSession() as session:
        requests = [session.get(url) for url in urls]
        responses = await asyncio.gather(*requests)
        for r in responses:
            html = await r.text()
            links.extend(parse_book_links(html))
            if not r.closed:
                await r.close()
        return links


async def worker(links, conn) -> list[BookInfoParsed]:
    await asyncio.sleep(random.uniform(0, 1))
    async with ClientSession() as session:
        tasks = [parse_and_save(session, link, conn) for link in links]
        books = await asyncio.gather(*tasks)
        return [b for b in books if b is not None]


async def parse_and_save(session, link, conn) -> Optional[BookInfoParsed]:
    async with session.get(link) as response:
        html = await response.text()
        details = parse_book_details(html)
        err = await conn.add_book(details, source="from async")
        if err is not None:
            print(err)
            return None
        return details
