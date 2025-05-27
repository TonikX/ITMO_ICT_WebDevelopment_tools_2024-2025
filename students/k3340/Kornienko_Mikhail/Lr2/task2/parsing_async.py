import asyncio
import time
from typing import List
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import aiohttp
from async_parser import parse_and_save, parse_and_save_async

URLS = [f'https://timus.online/problem.aspx?space=1&num={i}' for i in range(1000, 1100)]
db_url = 'postgresql+asyncpg://lr3:12345678@lr3_pg:5432/lr3'


async def async_run(urls):
    engine = create_async_engine(db_url, echo=False)
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with engine.begin() as conn:
        tasks = []
        for url in urls:
            tasks.append(parse_and_save_async(url, AsyncSessionLocal))
        await asyncio.gather(*tasks)

    await engine.dispose()


def run(urls):
    async def _wrap():
        start = time.perf_counter()
        await async_run(urls)
        return time.perf_counter() - start

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_wrap())
    else:
        return _wrap()


async def main():
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, url) for url in URLS]
        await asyncio.gather(*tasks)
    print(f"Total execution time: {time.time() - start:.2f} seconds")


if __name__ == '__main__':
    asyncio.run(main())
