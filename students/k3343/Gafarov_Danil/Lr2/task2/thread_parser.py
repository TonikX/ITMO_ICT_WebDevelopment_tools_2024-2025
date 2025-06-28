# parser_thread.py

import requests
from threading import Thread
from config import SITE_URL, CHUNKS, CHUNK_SIZE
from database import User, get_session

def fetch_and_save():
    response = requests.get(f"{SITE_URL}{CHUNK_SIZE}")
    data = response.json()["results"]

    users = [{
        "email": item["email"],
        "username": item["login"]["username"]
    } for item in data]

    with get_session() as session:
        existing_emails = {u.email for u in session.query(User).all()}
        new_users = [User(**u) for u in users if u["email"] not in existing_emails]
        session.add_all(new_users)
        session.commit()
        print(f"[Threading] Сохранено: {len(new_users)} пользователей")

def run_threads():
    threads = [Thread(target=fetch_and_save) for _ in range(CHUNKS)]
    start = time.time()

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    end = time.time()
    print(f"[Threading] Время: {end - start:.2f} секунд")

if __name__ == "__main__":
    from database import clear_users
    import time

    clear_users()

    run_threads()