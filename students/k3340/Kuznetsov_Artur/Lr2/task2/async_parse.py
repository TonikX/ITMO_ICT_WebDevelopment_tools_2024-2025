import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup
from passlib.context import CryptContext
from models import Users
from sqlmodel import Session
from connection import engine

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")


async def parse_and_save(url):
    try:
        # Загрузка страницы
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

        # Извлечение username
        username_tag = soup.find("a", class_ = "tm-user-card__nickname")
        if not username_tag:
            raise ValueError("No username found")
        base_username = username_tag.text.strip().lstrip('@')
        username = f"{base_username}_async"

        # Формирование email и password
        email = f"{username}@async.ru"
        hashed_password = pwd_context.hash(base_username)

        # Извлечение имени и фамилии
        name_tag = soup.find("span", class_ = "tm-user-card__name")
        if not name_tag:
            raise ValueError("No name found")
        full_name = name_tag.text.strip()
        name_parts = full_name.split()
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else "Unknown"

        # Сохранение в базу данных
        with Session(engine) as session:
            user = Users(
                username = username,
                password = hashed_password,
                first_name = first_name,
                last_name = last_name,
                email = email
            )
            session.add(user)
            session.commit()
        print(f"Async: User added {username} ({first_name} {last_name})")
    except Exception as e:
        print(f"Async: Error {url}: {e}")


async def main(urls):
    start_time = time.time()
    await asyncio.gather(*(parse_and_save(url) for url in urls))
    end_time = time.time()
    print(f"Time: {end_time - start_time:.2f} seconds")
