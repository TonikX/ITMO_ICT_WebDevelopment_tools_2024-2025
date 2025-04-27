import asyncio
import json
import time
import uuid

import aiohttp
from bs4 import BeautifulSoup

from auth import hash_password
from db.database import init_db, get_session
from db.models import Page, User

URLS = [
    "https://www.team2.travel/id96206",
    "https://www.team2.travel/id81971",
    "https://www.team2.travel/id96205",
    "https://www.team2.travel/id93029",
    "https://www.team2.travel/id79568",
    "https://www.team2.travel/id96209",
    "https://www.team2.travel/id26208",
    "https://www.team2.travel/id96142",
    "https://www.team2.travel/id96150",
    "https://www.team2.travel/id18195"
]
PARTS = 4


def sync_save(url: str, title: str, user_fields: dict, prefix: str):
    session_gen = get_session()
    session = next(session_gen)
    try:
        page = Page(url=url, title=title)
        session.add(page)

        user = User(
            username=user_fields['username'],
            email=user_fields['email'],
            first_name=user_fields['first_name'],
            last_name=user_fields['last_name'],
            age=user_fields['age'],
            description=user_fields['description'],
            password_hash=user_fields['password_hash']
        )
        session.add(user)
        session.commit()
        print(f"[{prefix}] Saved user {user.username} and page title {title!r}")
    except Exception as e:
        print(f"[{prefix}] DB error for {url}: {e}")
    finally:
        try:
            session.close()
        except:
            pass


async def parse_and_prepare(url: str, prefix: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=10) as resp:
            resp.raise_for_status()
            html = await resp.text()
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string.strip() if soup.title and soup.title.string else None

        segment = url.rstrip('/').split('/')[-1]
        user_id = segment[2:] if segment.startswith('id') else segment
        api_url = "https://www.team2.travel/user"
        params = {"Task": "GetUser", "id_user": user_id}
        async with session.get(api_url, params=params, timeout=10) as r2:
            r2.raise_for_status()
            text = await r2.text(encoding='windows-1251')
            data = json.loads(text)
        user_data = data.get('InUser', {})

        first_name = user_data.get('firstname')
        last_name = user_data.get('family')
        age = None
        if 'setage' in user_data and user_data['setage'] is not None:
            try:
                age = int(user_data['setage'])
            except (ValueError, TypeError):
                age = None
        description = user_data.get('about')

        username = f"{prefix}_{uuid.uuid4().hex[:8]}"
        email = f"{uuid.uuid4().hex}@example.com"
        pwd_hash = hash_password('DefaultPass123')

        user_fields = {
            'first_name': first_name,
            'last_name': last_name,
            'age': age,
            'description': description,
            'username': username,
            'email': email,
            'password_hash': pwd_hash
        }

        return url, title, user_fields


async def async_worker(urls: list, prefix: str):
    for url in urls:
        try:
            url, title, user_fields = await parse_and_prepare(url, prefix)
            await asyncio.to_thread(sync_save, url, title, user_fields, prefix)
        except Exception as e:
            print(f"[{prefix}] Error processing {url}: {e}")


def chunks(lst: list, n: int) -> list:
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


async def main_async():
    init_db()
    url_chunks = chunks(URLS, PARTS)
    tasks = []
    for i, chunk in enumerate(url_chunks):
        prefix = f"async{i}"
        tasks.append(asyncio.create_task(async_worker(chunk, prefix)))
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    t0 = time.time()
    asyncio.run(main_async())
    print(f"Asyncio parser finished in {time.time() - t0:.2f} seconds")
