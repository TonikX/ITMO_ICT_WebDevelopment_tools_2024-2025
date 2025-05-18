import multiprocessing
import time

from students.k3342.Smirnova_Glafira.lr_2.task2_parsing.parser import *


def multiprocessing_approach():
    start_time = time.time()

    init_db()

    multiprocessing.set_start_method('spawn', force=True)

    processes = []
    for url in GENRE_URLS:
        process = multiprocessing.Process(
            target=parse_genre_page,
            args=(url,)
        )
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    logger.info(f"Multiprocessing завершён за {time.time() - start_time:.2f} сек")


if __name__ == "__main__":
    multiprocessing_approach()
