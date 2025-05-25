import time
from multiprocessing import Process

from parse.parse_utils import urls, chunkify, worker

NUM_PROCESSORS = 5


def main():
    url_chunks = chunkify(urls, NUM_PROCESSORS)
    processes = []
    for chunk in url_chunks:
        p = Process(target=worker, args=(chunk,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()


if __name__ == "__main__":
    start_time = time.time()
    main()
    duration = time.time() - start_time
    print(f"Затрачено времени: {duration:.2f} секунд")
