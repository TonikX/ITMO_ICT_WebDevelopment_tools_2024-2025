# multiprocessing_parser.py
import multiprocessing
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
import hashlib
import re
from models import User
from db import SyncSession, init_sync_db


def init_process():
    init_sync_db()


def parse_and_save(args):
    url, suffix = args
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
                hashed_password=hashlib.sha256(
                    f"fake{base_username}{random.randint(1, 1000)}".encode()
                ).hexdigest(),
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

    suffix = "_mp"
    start = time.time()

    with multiprocessing.Pool(
            4,
            initializer=init_process
    ) as pool:
        pool.map(parse_and_save, [(url, suffix) for url in urls])

    print(f"Multiprocessing time: {time.time() - start:.2f}s")


if __name__ == "__main__":
    main()