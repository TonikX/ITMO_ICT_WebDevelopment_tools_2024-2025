import asyncio
import asyncpg
import time
from db import async_save_bus, ASYNC_DSN
from fetching import async_fetch_html, URLS
from parser_utils import parse_car_types_from_html


async def worker(url: str, pool: asyncpg.Pool):
    html_content = await async_fetch_html(url)
    car_types = parse_car_types_from_html(html_content)
    await async_save_bus(car_types, pool)


async def main():
    pool = await asyncpg.create_pool(ASYNC_DSN)
    try:
        tasks = [asyncio.create_task(worker(url, pool)) for url in URLS]
        await asyncio.gather(*tasks)
    finally:
        await pool.close()


if __name__ == "__main__":
    start_time = time.perf_counter()
    asyncio.run(main())
    end_time = time.perf_counter()
    print(f"Async execution took: {end_time - start_time:.2f} seconds")