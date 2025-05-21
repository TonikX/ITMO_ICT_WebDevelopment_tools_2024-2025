import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup
from passlib.context import CryptContext
from models.finance_models import User
from sqlmodel.ext.asyncio.session import AsyncSession
from db.connection import engine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def fetch_html(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url, timeout=10) as response:
        response.raise_for_status()
        return await response.text()


async def parse_and_save(session: aiohttp.ClientSession, url: str) -> None:
    try:
        html = await fetch_html(session, url)
        soup = BeautifulSoup(html, "html.parser")

        username_tag = soup.select_one("a.tm-user-card__nickname")
        if not username_tag:
            raise ValueError("Username not found")
        base_username = username_tag.text.strip().lstrip("@")
        username = f"{base_username}_async"
        email = f"{username}@async.ru"
        hashed_password = pwd_context.hash(base_username)

        name_tag = soup.select_one("span.tm-user-card__name")
        if name_tag:
            name_parts = name_tag.text.strip().split()
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else "Unknown"
        else:
            first_name = base_username
            last_name = "Unknown"

        async with AsyncSession(engine) as db:
            user = User(
                username=username,
                hashed_password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            db.add(user)
            await db.commit()

        print(f"Async: User added {username} ({first_name} {last_name})")

    except Exception as e:
        print(f"Async: Error {url}: {e}")



async def main(urls: list[str]) -> None:
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*(parse_and_save(session, url) for url in urls))
    print(f"Time: {time.time() - start_time:.2f} seconds")
