import time
import requests
import logging
from multiprocessing import Pool, current_process, cpu_count
from parser import save_sync
from db import init_db
from urls import urls


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(processName)s | %(levelname)s | %(message)s'
)


def fetch_and_save(link):
    try:
        logging.info(f"Fetching: {link}")
        resp = requests.get(link, timeout=10)
        resp.raise_for_status()
        save_sync(resp.text)
        logging.info(f"Saved data from: {link}")
    except requests.RequestException as err:
        logging.error(f"Failed to process {link}: {err}")


def run_parallel():
    init_db()
    workers = min(4, cpu_count())
    logging.info(f"Using {workers} worker(s)")

    with Pool(processes=workers) as pool:
        pool.map(fetch_and_save, urls)


if __name__ == "__main__":
    t0 = time.perf_counter()
    logging.info("Begin parsing")
    run_parallel()
    t1 = time.perf_counter()
    logging.info(f"Completed in {t1 - t0:.3f} seconds")

#Completed in 2.177 seconds