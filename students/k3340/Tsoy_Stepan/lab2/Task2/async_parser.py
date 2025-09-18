import time
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from db_utils import save_title_to_db

URLS = [
    "https://store.steampowered.com/",
    "https://www.nalog.gov.ru/",
    "https://worldoftanks.eu/",
    "https://itmo.ru/",
    "https://www.aviasales.ru/",
]

async def fetch(session, url):
    async with session.get(url, timeout=10) as resp:
        return await resp.text()

async def parse_and_save(url):
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title else "No title"
        save_title_to_db(title)
        print(f"[async] {url} -> {title}")

async def main():
    start = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in URLS:
            tasks.append(asyncio.create_task(parse_and_save(url)))
        await asyncio.gather(*tasks)
    print(f"[async] Finished in {time.perf_counter() - start:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
