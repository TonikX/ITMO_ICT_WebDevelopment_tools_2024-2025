import multiprocessing
import time
from db import sync_save_bus
from fetching import sync_fetch_html, URLS
from parser_utils import parse_car_types_from_html


def worker(url: str):
    html_content = sync_fetch_html(url)
    car_types = parse_car_types_from_html(html_content)
    sync_save_bus(car_types)


def main():
    processes = [multiprocessing.Process(target=worker, args=(url,)) for url in URLS]
    for p in processes:
        p.start()
    for p in processes:
        p.join()


if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    print(f"Multiprocessing execution took: {end_time - start_time:.2f} seconds")