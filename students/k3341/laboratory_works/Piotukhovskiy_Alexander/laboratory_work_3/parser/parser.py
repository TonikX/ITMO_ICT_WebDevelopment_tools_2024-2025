import json
import uuid

import aiohttp
from bs4 import BeautifulSoup

from auth import hash_password
from db.database import AsyncSessionLocal
from db.models import Page, User


async def async_save(url: str, title: str, user_fields: dict, prefix: str):
    async with AsyncSessionLocal() as session:
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
            await session.commit()
            print(f"[{prefix}] Saved user {user.username} and page title {title!r}")
        except Exception as e:
            print(f"[{prefix}] DB error for {url}: {e}")
        finally:
            try:
                await session.close()
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


async def save_page(url: str, prefix: str):
    try:
        url, title, user_fields = await parse_and_prepare(url, prefix)
        await async_save(url, title, user_fields, prefix)
    except Exception as e:
        print(f"[{prefix}] Error processing {url}: {e}")
        raise
