import sys
import os

os.environ["APP_ENV"] = "parsers"  # Важно для настроек БД

import traceback
import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup
import random
import hashlib
import re
from common.models.user import User
from db import AsyncSessionLocal, init_async_db
import json


async def generate_fake_password(username):
    return hashlib.sha256(f"fake{username}{random.randint(1, 1000)}".encode()).hexdigest()


async def parse_and_save(session, url, suffix, results):
    try:
        print(f"Starting parse of {url}...", file=sys.stderr)
        async with session.get(url) as response:
            response.raise_for_status()
            html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')
        page_text = soup.get_text()

        # Попытка найти имя пользователя и имя из заголовка страницы или метаданных
        username_match = re.search(r"(\w+)\s+\(([^)]+)\)", page_text)  # Пример для GitHub
        base_username = username_match.group(1) if username_match else url.split('/')[-1].replace('-', '_')
        name = username_match.group(2) if username_match else "Unknown"

        if not base_username:  # Если URL не заканчивается на имя, используем хэш
            base_username = hashlib.md5(url.encode()).hexdigest()[:10]

        async with AsyncSessionLocal() as db_session:
            user = User(
                username=f"{base_username}{suffix}",
                name=name,
                email=f"{base_username}{suffix}@example.com",
                hashed_password=await generate_fake_password(base_username)
            )
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)  # Обновим объект, чтобы получить id из БД
            print(f"Saved: {user.username} (ID: {user.user_id}) from {url}", file=sys.stderr)
            results.append({"username": user.username, "name": user.name, "email": user.email, "id": user.user_id})

    except aiohttp.ClientError as e:
        print(f"HTTP Error processing {url}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error processing {url}: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        results.append(None)


async def main(target_urls: list[str], suffix: str):  # Принимаем список URL
    await init_async_db()

    start = time.time()

    results = []  # Список для хранения результатов парсинга
    async with aiohttp.ClientSession() as http_session:
        tasks = [parse_and_save(http_session, url, suffix, results) for url in target_urls]
        await asyncio.gather(*tasks)

    print(f"Async time for {len(target_urls)} URLs: {time.time() - start:.2f}s", file=sys.stderr)
    print(json.dumps({"parsed_users": results, "time_taken_seconds": round(time.time() - start, 2)}))


if __name__ == "__main__":
    # sys.argv[0] - имя скрипта
    # sys.argv[1] - первый аргумент (URL)
    if len(sys.argv) < 2:
        print("Usage: python async_parser.py <url_to_parse_1> [url_to_parse_2 ...]", file=sys.stderr)
        sys.exit(1)

    urls_from_cli = sys.argv[1:]

    asyncio.run(main(urls_from_cli, "_async"))  # Передаем URL в main как список