import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from models import Task
from db import get_session, create_db_and_tables
from urls import URLS
import time

async def parse_and_save(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            headings = []
            for tag in ["h1", "h2", "h3"]:
                for elem in soup.find_all(tag):
                    text = elem.get_text(strip=True)
                    if text:
                        headings.append(text)

            if not headings:
                headings = ["Заголовков не найдено"]

            deadline = datetime.utcnow() + timedelta(days=3)
            with get_session() as db_session:
                for title in headings:
                    task = Task(
                        title=title[:255],
                        description=url,
                        deadline=deadline,
                        priority="high",
                        owner_id=1
                    )
                    db_session.add(task)
                db_session.commit()

            print(f"[Async] {url} → {', '.join(headings)}")
    except Exception as e:
        print(f"[Async] Error processing {url}: {e}")

async def main_async():
    create_db_and_tables()
    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, url) for url in URLS]
        await asyncio.gather(*tasks)

def main():
    start_time = time.time()
    asyncio.run(main_async())
    duration = time.time() - start_time
    print(f"Async {duration:.2f} seconds")

if __name__ == "__main__":
    main()
