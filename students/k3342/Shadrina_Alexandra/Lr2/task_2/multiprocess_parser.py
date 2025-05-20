import multiprocessing
import time
from db import parse_and_save
from base import urls


def process_parse_and_save(url, genre):
    parse_and_save(url, genre)


def run_with_multiprocessing():
    start_time = time.time()

    processes = []
    for genre, url in urls.items():
        process = multiprocessing.Process(target=process_parse_and_save, args=(url, genre))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    end_time = time.time()
    print(f"Multiprocessing time: {end_time - start_time} секунд")


if __name__ == "__main__":
    run_with_multiprocessing()
