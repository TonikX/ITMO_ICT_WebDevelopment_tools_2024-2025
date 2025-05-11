import asyncio
import time
import aiohttp
from parse_and_save_async import parse_and_save_async

urls = [
    "https://sletat.ru/tours/turkey/",
    "https://sletat.ru/tours/uae/",
    "https://sletat.ru/tours/egypt/",
    "https://sletat.ru/tours/vietnam/",
    "https://sletat.ru/tours/thailand/",
    "https://sletat.ru/tours/maldives/",
    "https://sletat.ru/tours/russia/",
    "https://sletat.ru/tours/cuba/",
    "https://sletat.ru/tours/sri_lanka/",
    "https://sletat.ru/tours/china/",
    "https://sletat.ru/tours/abkhazia/",
]

async def main():
    start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save_async(session, url) for url in urls]
        await asyncio.gather(*tasks)
    print(f"Async total time: {time.time() - start:.2f}s")

if __name__ == '__main__':
    asyncio.run(main())
