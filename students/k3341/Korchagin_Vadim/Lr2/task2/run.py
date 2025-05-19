import asyncio
import aiohttp
from bs4 import BeautifulSoup

import threading_
import multiprocessing_
import async_
from db.connection import init_db


async def extract_user_links(page_url: str) -> list[str]:
    async with aiohttp.ClientSession() as session:
        async with session.get(page_url, timeout=10) as response:
            response.raise_for_status()
            html = await response.text()

    soup = BeautifulSoup(html, "html.parser")
    return [
        "https://habr.com" + a["href"]
        for a in soup.select("a.tm-user-snippet__nickname")
        if a.get("href")
    ]


async def run_all():
    await init_db()

    base_url = "https://habr.com/ru/users/"
    user_urls = await extract_user_links(base_url)

    if not user_urls:
        print("No user URLs found.")
        return

    print(f"Parsed {len(user_urls)} user URLs")
    await async_.main(user_urls)


if __name__ == "__main__":
    asyncio.run(run_all())
