import time
import asyncio
import aiohttp
from parser import async_parse_and_save_page
from db import async_init_db
from urls import urls

async def fetch(session, url):
    async with session.get(url, timeout=10, ssl=False) as response:
        html_data = await response.text()
        return html_data


async def _parse_and_save(url):
    async with aiohttp.ClientSession() as session:
        html_data = await fetch(session, url)
        if html_data:
            await async_parse_and_save_page(html_data)


async def parse_chunk(chunk):
    tasks = [_parse_and_save(url) for url in chunk]
    await asyncio.gather(*tasks)


async def main():
    await async_init_db()

    num_chunks = 3
    chunk_size = (len(urls) + num_chunks - 1) // num_chunks
    chunks = [urls[i:i+chunk_size] for i in range(0, len(urls), chunk_size)]

    chunk_tasks = [parse_chunk(chunk) for chunk in chunks]
    await asyncio.gather(*chunk_tasks)


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Time (sec): {end_time - start_time:.6f}")