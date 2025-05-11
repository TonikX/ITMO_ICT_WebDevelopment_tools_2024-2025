import asyncio
import time
import aiohttp
from async_parser import parse_and_save

urls = [f'https://timus.online/problem.aspx?space=1&num={i}' for i in range(1000, 1100)]


async def main():
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, url) for url in urls]
        await asyncio.gather(*tasks)
    print(f"Total execution time: {time.time() - start:.2f} seconds")

if __name__ == '__main__':
    asyncio.run(main())