# parser_async.py

import asyncio
import aiohttp
from config import SITE_URL, CHUNKS, CHUNK_SIZE
from database import User, get_session

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()

def extract_users(data):
    return [{
        "email": item["email"],
        "username": item["login"]["username"]
    } for item in data["results"] if isinstance(item, dict)]

async def main():
    urls = [f"{SITE_URL}{CHUNK_SIZE}" for _ in range(CHUNKS)]

    async with aiohttp.ClientSession() as http_session:
        tasks = [fetch(http_session, url) for url in urls]
        results = await asyncio.gather(*tasks)

    all_users = []
    for data in results:
        all_users.extend(extract_users(data))

    with get_session() as session:
        existing_emails = {u.email for u in session.query(User).all()}
        new_users = [User(**u) for u in all_users if u["email"] not in existing_emails]

        session.add_all(new_users)
        session.commit()
        print(f"[Async] Сохранено: {len(new_users)} пользователей")

if __name__ == "__main__":
    import time
    from database import clear_users
    clear_users()

    start = time.time()
    asyncio.run(main())
    end = time.time()
    print(f"[Async] Время: {end - start:.2f} секунд")