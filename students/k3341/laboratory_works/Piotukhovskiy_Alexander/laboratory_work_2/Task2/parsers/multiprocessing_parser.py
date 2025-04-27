import multiprocessing
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


def parse_and_save(url: str, prefix: str):
    session_gen = get_session()
    session = next(session_gen)
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string.strip() if soup.title and soup.title.string else None

        page = Page(url=url, title=title)
        session.add(page)
        print(f"[{prefix}] Saved page title: {title!r} from {url}")

        segment = url.rstrip('/').split('/')[-1]
        user_id = segment[2:] if segment.startswith('id') else segment
        api_url = "https://www.team2.travel/user"
        params = {"Task": "GetUser", "id_user": user_id}
        r2 = requests.get(api_url, params=params, timeout=10)
        r2.raise_for_status()
        user_data = r2.json().get('InUser', {})

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
            print(f"[{prefix}] Warning: empty JSON fields for user {user_id}")

        username = f"{prefix}_{uuid.uuid4().hex[:8]}"
        email = f"{uuid.uuid4().hex}@example.com"
        pwd_hash = hash_password('DefaultPass123')

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            age=age,
            description=description,
            password_hash=pwd_hash
        )
        session.add(user)
        session.commit()
        print(f"[{prefix}] Saved user {username} (id {user_id})")

    except Exception as e:
        print(f"[{prefix}] Error processing {url}: {e}")
    finally:
        try:
            session.close()
        except:
            pass


def worker(chunk: list, prefix: str):
    for url in chunk:
        parse_and_save(url, prefix)


def chunks(lst: list, n: int) -> list:
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


def main():
    init_db()

    url_chunks = chunks(URLS, PARTS)
    processes = []
    start = time.time()

    for i, chunk in enumerate(url_chunks):
        prefix = f"proc{i}"
        p = multiprocessing.Process(target=worker, args=(chunk, prefix), daemon=True)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    duration = time.time() - start
    print(f"Multiprocessing parser finished in {duration:.2f} seconds")


if __name__ == '__main__':
    main()
