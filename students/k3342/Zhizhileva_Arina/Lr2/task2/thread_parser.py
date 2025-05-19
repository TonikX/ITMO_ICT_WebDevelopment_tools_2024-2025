import threading
import time
from db import parse_and_save
from base import urls


def thread_parse_and_save(url, genre):
    parse_and_save(url, genre)


def run_with_threading():
    start_time = time.time()

    threads = []
    for genre, url in urls.items():
        thread = threading.Thread(target=thread_parse_and_save, args=(url, genre))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    print(f"Threading time: {end_time - start_time} секунд")


if __name__ == "__main__":
    run_with_threading()
