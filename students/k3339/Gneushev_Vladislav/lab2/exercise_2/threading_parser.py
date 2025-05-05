import threading
import time
from db import sync_save_bus
from fetching import sync_fetch_html, URLS
from parser_utils import parse_car_types_from_html


def worker(url: str):
    html_content = sync_fetch_html(url)
    car_types = parse_car_types_from_html(html_content)
    sync_save_bus(car_types)


def main():
    threads = [threading.Thread(target=worker, args=(url,)) for url in URLS]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    print(f"Threading execution took: {end_time - start_time:.2f} seconds")