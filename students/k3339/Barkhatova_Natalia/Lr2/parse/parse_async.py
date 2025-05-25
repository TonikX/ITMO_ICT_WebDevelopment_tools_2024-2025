import asyncio
import sys
import time

import aiohttp
from bs4 import BeautifulSoup

from parse.db import save_to_db
from parse.parse_utils import urls, chunkify, parse_title_author

NUM_TASKS = 5

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def fetch(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            text = await response.text()
            return url, text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return url, None


async def parse_and_save_async(session, url):
    url, html = await fetch(session, url)
    if not html:
        print(f"Failed to get content for {url}")
        return

    soup = BeautifulSoup(html, "html.parser")
    full_title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
    title, author = parse_title_author(full_title)

    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, save_to_db, url, title, author)
        print(f"{url} -> title: {title}, author: {author}")
    except Exception as e:
        print(f"Error saving {url}: {e}")


async def worker(url_subset, session):
    tasks = [parse_and_save_async(session, url) for url in url_subset]
    await asyncio.gather(*tasks)


async def main():
    url_chunks = chunkify(urls, NUM_TASKS)
    async with aiohttp.ClientSession() as session:
        tasks = [worker(chunk, session) for chunk in url_chunks]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()
    print(f"Затрачено времени: {end - start:.2f} секунд")
