import time
import multiprocessing
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

    num_processes = 3
    chunk_size = (len(urls) + num_processes - 1) // num_processes
    chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]
    processes = []

    for chunk in chunks:
        process = multiprocessing.Process(target=_parse_and_save, args=(chunk,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Time (sec): {end_time - start_time:.6f}")