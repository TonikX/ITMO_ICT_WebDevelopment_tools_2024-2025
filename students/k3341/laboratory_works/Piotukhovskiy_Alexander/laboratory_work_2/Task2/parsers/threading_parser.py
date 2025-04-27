import threading
import time
import uuid

import requests
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


def parse_and_save(url: str, username_prefix: str):
    session_gen = get_session()
    session = next(session_gen)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        page_title = None
        if soup.title and soup.title.string:
            page_title = soup.title.string.strip()

        page = Page(url=url, title=page_title)
        session.add(page)
        print(f"[{username_prefix}] Saved page title: {page_title!r} from {url}")

        segment = url.rstrip('/').split('/')[-1]
        user_id = segment[2:] if segment.startswith('id') else segment
        api_url = f"https://www.team2.travel/user"
        params = {"Task": "GetUser", "id_user": user_id}
        resp = requests.get(api_url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
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

        if not any([first_name, last_name, age, description]):
            print(f"[{username_prefix}] Warning: empty JSON fields for user {user_id}")

        username = f"{username_prefix}_{uuid.uuid4().hex[:8]}"
        email = f"{uuid.uuid4().hex}@example.com"
        password_hash = hash_password('DefaultPass123')

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            age=age,
            description=description,
            password_hash=password_hash
        )
        session.add(user)
        session.commit()
        print(f"[{username_prefix}] Saved user {username} (id {user_id}) via API")

    except Exception as e:
        print(f"[{username_prefix}] Error processing {url}: {e}")
    finally:
        try:
            session.close()
        except:
            pass


def worker(urls: list[str], username_prefix: str):
    for url in urls:
        parse_and_save(url, username_prefix)


def chunks(lst: list, n: int) -> list[list]:
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


def main():
    init_db()

    url_chunks = chunks(URLS, PARTS)
    threads = []
    start_time = time.time()

    for idx, chunk in enumerate(url_chunks, start=1):
        prefix = f"thread{idx}"
        thread = threading.Thread(target=worker, args=(chunk, prefix), daemon=True)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    duration = time.time() - start_time
    print(f"Threading parser finished in {duration:.2f} seconds")


if __name__ == "__main__":
    main()
