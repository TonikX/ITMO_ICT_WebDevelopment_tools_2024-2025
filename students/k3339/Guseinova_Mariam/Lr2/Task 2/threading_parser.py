# threading_parser.py
import threading
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
import hashlib
import re
from models import User
from db import SyncSession, init_sync_db

init_sync_db()


def generate_fake_password(username):
    return hashlib.sha256(f"fake{username}{random.randint(1, 1000)}".encode()).hexdigest()


def parse_and_save(url, suffix):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        username_match = re.search(r"(\w+)\s+\(([^)]+)\)", page_text)
        base_username = username_match.group(1) if username_match else url.split('/')[-1]
        name = username_match.group(2) if username_match else "Unknown"

        with SyncSession() as session:
            user = User(
                username=f"{base_username}{suffix}",
                name=name,
                email=f"{base_username}{suffix}@example.com",
                hashed_password=generate_fake_password(base_username),
                registration_date=datetime.now()
            )
            session.add(user)
            session.commit()
            print(f"Saved: {user.username}")
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")


def main():
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

    suffix = "_thread"
    num_threads = 4
    chunk_size = (len(urls) + num_threads - 1) // num_threads

    start = time.time()

    threads = []
    for i in range(num_threads):
        chunk = urls[i * chunk_size: (i + 1) * chunk_size]
        t = threading.Thread(
            target=lambda urls: [parse_and_save(u, suffix) for u in urls],
            args=(chunk,)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"Threading time: {time.time() - start:.2f}s")


if __name__ == "__main__":
    main()