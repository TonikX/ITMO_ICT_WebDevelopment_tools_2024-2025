import asyncio
import aiohttp
import ssl
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from sqlmodel import SQLModel, Session, create_engine
from models import Preference  # Импортируй свою модель Preference

load_dotenv()

DATABASE_URL = os.getenv("DB_ADMIN")
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

urls = [
    "https://www.tourradar.com/i/beach",
    "https://www.tourradar.com/i/culture",
    "https://www.tourradar.com/i/adventure",
    "https://www.tourradar.com/i/trekking",
    "https://www.tourradar.com/i/wildlife",
    "https://www.tourradar.com/i/sightseeing"
]

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def parse_and_save(session, url):
    try:
        async with session.get(url, ssl=ssl_context) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            name = url.split("/")[-1].capitalize()

            with Session(engine) as db:
                pref = Preference(name=name)
                db.add(pref)
                db.commit()
                print(f"[OK] Saved preference: {name}")

    except Exception as e:
        print(f"[ERROR] {url}: {e}")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, url) for url in urls]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    import time
    start = time.time()
    asyncio.run(main())
    print(f"Finished in {time.time() - start:.2f} seconds")
