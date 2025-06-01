import threading
import time

from parse.parse_utils import urls, chunkify, worker

NUM_THREADS = 5


def main():
    url_chunks = chunkify(urls, NUM_THREADS)
    threads = []
    for chunk in url_chunks:
        thread = threading.Thread(target=worker, args=(chunk,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    start_time = time.time()
    main()
    duration = time.time() - start_time
    print(f"Затрачено времени: {duration:.2f} секунд")
