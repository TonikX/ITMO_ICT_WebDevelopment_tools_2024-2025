import threading
import time

from students.k3342.Smirnova_Glafira.lr_2.task2_parsing.parser import *


def threading_approach():
    start_time = time.time()
    engine = init_db()

    threads = []

    for url in GENRE_URLS:
        thread = threading.Thread(target=parse_genre_page, args=(url, engine, ))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    logger.info(f"Threading завершён за {time.time() - start_time:.2f} сек")


if __name__ == "__main__":
    threading_approach()