# parser_multi.py

import multiprocessing
import requests
from config import SITE_URL, CHUNKS, CHUNK_SIZE
from database import User, get_session


def fetch_users(_):
    response = requests.get(f"{SITE_URL}{CHUNK_SIZE}")
    return response.json()["results"]


def save_chunk(data_list):
    with get_session() as session:
        for item in data_list:
            user = {
                "email": item["email"],
                "username": item["login"]["username"]
            }
            db_user = User(**user)
            existing = session.query(User).filter(User.email == db_user.email).first()
            if not existing:
                session.add(db_user)
        session.commit()


def run_multiprocessing():
    with multiprocessing.Pool(2) as pool:
        all_results = pool.map(fetch_users, range(CHUNKS))

    flat_results = [item for sublist in all_results for item in sublist]

    with get_session() as session:
        existing_emails = {u.email for u in session.query(User).all()}
        new_users = [u for u in flat_results if u["email"] not in existing_emails]

        with multiprocessing.Pool(2) as pool:
            pool.map(save_chunk, [new_users[i::2] for i in range(2)])

    print(f"[Multiprocessing] Сохранено: {len(new_users)} пользователей")


if __name__ == "__main__":
    from database import clear_users
    import time

    clear_users()
    start = time.time()
    run_multiprocessing()
    end = time.time()
    print(f"[Multiprocessing] Время: {end - start:.2f} секунд")