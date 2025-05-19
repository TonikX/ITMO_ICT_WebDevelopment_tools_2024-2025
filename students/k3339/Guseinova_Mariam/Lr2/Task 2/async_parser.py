# async_parser.py
import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup
from datetime import datetime
import random
import hashlib
import re
from models import User
from db import AsyncSessionLocal, init_async_db, async_engine


async def generate_fake_password(username):
    return hashlib.sha256(f"fake{username}{random.randint(1, 1000)}".encode()).hexdigest()


async def parse_and_save(session, url, suffix):
    try:
        async with session.get(url) as response:
            html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')
        page_text = soup.get_text()

        username_match = re.search(r"(\w+)\s+\(([^)]+)\)", page_text)
        base_username = username_match.group(1) if username_match else url.split('/')[-1]
        name = username_match.group(2) if username_match else "Unknown"

        async with AsyncSessionLocal() as db_session:
            user = User(
                username=f"{base_username}{suffix}",
                name=name,
                email=f"{base_username}{suffix}@example.com",
                hashed_password=await generate_fake_password(base_username),
                registration_date=datetime.now()
            )
            db_session.add(user)
            await db_session.commit()
            print(f"Saved: {user.username}")

    except Exception as e:
        print(f"Error processing {url}: {str(e)}")


async def main():
    await init_async_db()

    urls = [
        "https://github.com/torvalds",
        "https://github.com/gaearon",
        "https://github.com/dhh",
        "https://github.com/mojombo",
        "https://github.com/fabpot",
        "https://github.com/defunkt",
        "https://github.com/mitsuhiko",
        "https://github.com/jashkenas",
        "https://github.com/rasbt",
        "https://github.com/zzzeek",
    ]

    suffix = "_async"
    start = time.time()

    async with aiohttp.ClientSession() as http_session:
        tasks = [parse_and_save(http_session, url, suffix) for url in urls]
        await asyncio.gather(*tasks)

    print(f"Async time: {time.time() - start:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())