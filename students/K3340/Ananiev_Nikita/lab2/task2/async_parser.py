import asyncio
import random
import time

from aiohttp import ClientSession
from helpers import tpl, base, parse_book_links, parse_book_details
from database import AsyncDBFiller

filler = AsyncDBFiller()
counter_lock = asyncio.Lock()
books_count = 100
books_saved = 0
workers_count = 4


async def get_books_links(urls):
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


async def worker(links):
    await asyncio.sleep(random.uniform(0, 1))
    async with ClientSession() as session:
        tasks = [parse_and_save(session, link) for link in links]
        await asyncio.gather(*tasks)


async def parse_and_save(session, link):
    global books_saved
    async with session.get(link) as response:
        html = await response.text()
        details = parse_book_details(html)
        err = await filler.add_book(details, source="from async")
        if err is None:
            async with counter_lock:
                books_saved += 1


async def main():
    await filler.connect()
    pages = [base + tpl.format(index) for index in range(1, books_count + 1, 25)]
    all_links = await get_books_links(pages)
    per_worker = books_count // workers_count
    await asyncio.gather(*[worker(all_links[i:i + per_worker]) for i in range(0, books_count, per_worker)])
    await filler.disconnect()


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print("TIME PASSED:", time.time() - start, "seconds")
    print("BOOKS SAVED:", books_saved)
