import time
import asyncio
from aiohttp import ClientSession
from parser import tpl, base, parse_book_links, parse_book_details
from db import AsyncDBFiller

WORKERS = 4
BOOKS_TOTAL = 100

async def init_links(session: ClientSession) -> list[str]:
    pages = [base + tpl.format(i) for i in range(1, BOOKS_TOTAL+1, 25)]
    tasks = [session.get(url) for url in pages]
    links: list[str] = []
    for resp in await asyncio.gather(*tasks, return_exceptions=True):
        if isinstance(resp, Exception):
            continue
        html = await resp.text()
        links.extend(parse_book_links(html))
        await resp.release()
    return links

async def worker(chunk: list[str], session: ClientSession, filler: AsyncDBFiller) -> int:
    saved = 0
    for url in chunk:
        try:
            resp = await session.get(url)
            html = await resp.text()
            details = parse_book_details(html)
            if await filler.add_book(details, "async"):
                saved += 1
            await resp.release()
        except Exception:
            continue
    return saved

async def main():
    filler = AsyncDBFiller()
    await filler.connect()
    async with ClientSession() as session:
        all_links = await init_links(session)
        per = (len(all_links) + WORKERS - 1) // WORKERS
        tasks = [
            worker(all_links[i:i+per], session, filler)
            for i in range(0, len(all_links), per)
        ]
        t0 = time.time()
        results = await asyncio.gather(*tasks)
    await filler.disconnect()
    total = sum(results)
    print(f"[asyncio] saved {total} books in {time.time()-t0:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())