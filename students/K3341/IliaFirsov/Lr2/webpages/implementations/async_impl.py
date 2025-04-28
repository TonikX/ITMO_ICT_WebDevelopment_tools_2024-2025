import asyncio
from typing import List

import aiohttp
from bs4 import BeautifulSoup
from webpages.abstractions import ParserImplementation
from webpages.database import Database
from webpages.utils import ColorLog

db = Database()


class AsyncParser(ParserImplementation):
    async def worker(self, session: aiohttp.ClientSession, url: str, idx: int):
        print(ColorLog.yellow(f"[Task {idx}] Parsing {url}"))
        try:
            async with session.get(url, ssl=False, timeout=10) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                title = soup.title.string if soup.title else "No Title"
                db.insert_page(url, title)
                print(ColorLog.yellow(f"[Task {idx}] Saved '{title}' from {url}"))
        except Exception as e:
            print(ColorLog.yellow(f"[Task {idx}] Error parsing {url}: {e}"))

    async def parse_all(self, urls: List[str]):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for idx, url in enumerate(urls):
                tasks.append(self.worker(session, url, idx))
            await asyncio.gather(*tasks)

    def parse_and_save_all(self, urls: List[str], num_tasks: int):
        asyncio.run(self.parse_all(urls))
