import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from parser import save_sync
from db import init_db
from urls import urls


def fetch_and_save(url, session, retries=3):
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            save_sync(response.text)
            return
        except requests.RequestException as e:
            if attempt < retries - 1:
                continue
            print(f"Failed after {retries} attempts: {url} — {e}")


def run_threads():
    init_db()
    workers = min(10, len(urls))
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(fetch_and_save, url, session) for url in urls]
            for future in as_completed(futures):
                pass


if __name__ == "__main__":
    t0 = time.perf_counter()
    run_threads()
    t1 = time.perf_counter()
    print(f"Completed in {t1 - t0:.3f} seconds")

#Completed in 0.892 seconds