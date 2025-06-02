import sys
import os

os.environ["APP_ENV"] = "parsers"  # Важно для настроек БД

import threading
import time
import requests
from bs4 import BeautifulSoup
import random
import hashlib
import re
from common.models.user import User
from db import SyncSession, init_sync_db
import json
import traceback

init_sync_db()
print("Main thread initialized DB connection.", file=sys.stderr)


def generate_fake_password(username):
    return hashlib.sha256(f"fake{username}{random.randint(1, 1000)}".encode()).hexdigest()


def parse_and_save(url, suffix):
    user_data = None # Будем возвращать данные пользователя или None в случае ошибки
    try:
        print(f"Thread {threading.current_thread().name} starting parse of {url}...", file=sys.stderr)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        username_match = re.search(r"(\w+)\s+\(([^)]+)\)", page_text)
        base_username = username_match.group(1) if username_match else url.split('/')[-1].replace('-', '_')
        name = username_match.group(2) if username_match else "Unknown"

        if not base_username:  # Если URL не заканчивается на имя, используем хэш
            base_username = hashlib.md5(url.encode()).hexdigest()[:10]

        with SyncSession() as session:
            user = User(
                username=f"{base_username}{suffix}",
                name=name,
                email=f"{base_username}{suffix}@example.com",
                hashed_password=generate_fake_password(base_username)
            )
            session.add(user)
            session.commit()
            session.refresh(user)  # Обновим объект, чтобы получить id из БД
            print(f"Thread {threading.current_thread().name} saved: {user.username} (ID: {user.user_id}) from {url}", file=sys.stderr)
            user_data = {"username": user.username, "name": user.name, "email": user.email, "id": user.user_id}
            return user_data # Возвращаем структурированные данные
    except requests.exceptions.RequestException as e:
        print(f"Thread {threading.current_thread().name} HTTP Error processing {url}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Thread {threading.current_thread().name} Error processing {url}: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    return user_data # Возвращаем None в случае ошибки

def thread_worker(urls_chunk: list[str], suffix: str, results_list: list):
    for url in urls_chunk:
        result = parse_and_save(url, suffix)
        if result:
            results_list.append(result)


def main(target_urls: list[str], suffix: str):
    start = time.time()
    num_threads = 4

    chunk_size = (len(target_urls) + num_threads - 1) // num_threads

    threads = []
    # Создаем общий список для результатов, доступный для всех потоков
    all_results = []
    lock = threading.Lock()

    for i in range(num_threads):
        chunk = target_urls[i * chunk_size: (i + 1) * chunk_size]
        if not chunk:
            continue

        t = threading.Thread(
            target=thread_worker,
            args=(chunk, suffix, all_results),
            name=f"Worker-{i + 1}"
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()  # Ждем завершения всех потоков

    total_time = time.time() - start
    print(f"Threading time for {len(target_urls)} URLs: {total_time:.2f}s", file=sys.stderr)

    final_output = {"parsed_users": [r for r in all_results if r is not None], "time_taken_seconds": round(total_time, 2)}
    print(json.dumps(final_output))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python threading_parser.py <url_to_parse_1> [url_to_parse_2 ...]", file=sys.stderr)
        sys.exit(1)

    urls_from_cli = sys.argv[1:]

    main(urls_from_cli, "_thread")