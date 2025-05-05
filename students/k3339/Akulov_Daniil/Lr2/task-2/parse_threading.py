import time
import threading
from parser import parse_and_save_page
from db import init_db
import requests
from urls import urls

def _parse_and_save(url_list):
    for url in url_list:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        parse_and_save_page(response.text)


def main():
    init_db()

    num_threads = 3
    chunk_size = (len(urls) + num_threads - 1) // num_threads
    chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]

    threads = []
    for chunk in chunks:
        thread = threading.Thread(target=_parse_and_save, args=(chunk,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Time (sec): {end_time - start_time:.6f}")