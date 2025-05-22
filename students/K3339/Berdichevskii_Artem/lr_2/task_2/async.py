import aiohttp
import asyncio
import time
from bs4 import BeautifulSoup
from db import init_db, save_to_db


async def parse_and_save(session, url) :
    try :
        async with session.get(url) as response :
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            title = soup.title.string.strip() if soup.title else "No title"
            save_to_db(url, title)
            print(f"[Async] {url}: {title}")
    except Exception as e :
        print(f"[Async] Error parsing {url}: {e}")


async def main() :
    init_db()
    with open("urls.txt") as f :
        urls = [line.strip() for line in f.readlines()]

    start = time.time()
    async with aiohttp.ClientSession() as session :
        tasks = [parse_and_save(session, url) for url in urls]
        await asyncio.gather(*tasks)
    print(f"Async completed in {time.time() - start:.2f}s")


if __name__ == "__main__" :
    asyncio.run(main())