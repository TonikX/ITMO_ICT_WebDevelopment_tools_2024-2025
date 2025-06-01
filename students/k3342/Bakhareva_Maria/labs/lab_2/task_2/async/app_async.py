import os
import asyncio
import aiohttp
import asyncpg
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time

from db_async import create_user_record

load_dotenv()
DATABASE_URI = os.environ["DB_URL"]

BASE_URL = "https://itmo.ru"

LETTERS = [
    ("А", "/ru/personlist/192/letter_192.htm"),
    ("Б", "/ru/personlist/193/letter_193.htm"),
    ("В", "/ru/personlist/194/letter_194.htm"),
    ("Г", "/ru/personlist/195/letter_195.htm"),
    ("Д", "/ru/personlist/196/letter_196.htm"),
]

async def parse_and_save(session, pool, url):
    print(f"Fetching: {url}")

    try:
        async with session.get(url, timeout=10) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")

            people_links = soup.select("a.contact-pad.-person-list")
            async with pool.acquire() as conn:
                for person_link in people_links:
                    name_tag = person_link.select_one("h4.name")
                    if name_tag:
                        name = name_tag.get_text(strip=True)
                        if name:
                            await create_user_record(conn, name)

    except Exception as e:
        print(f"Error fetching/parsing {url}: {e}")

async def main():
    t0 = time.perf_counter()

    pool = await asyncpg.create_pool(DATABASE_URI, min_size=2, max_size=10)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _, path in LETTERS:
            url = BASE_URL + path
            tasks.append(parse_and_save(session, pool, url))

        await asyncio.gather(*tasks)
    await pool.close()

    t1 = time.perf_counter()
    print(f"Async parsing duration: {t1 - t0:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
