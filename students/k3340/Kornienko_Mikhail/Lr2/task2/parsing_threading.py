import threading
import time
from parser import parse_and_save

urls = [f'https://timus.online/problem.aspx?space=1&num={i}' for i in range(1000, 1100)]


def process_urls(urls):
    for url in urls:
        parse_and_save(url)


if __name__ == '__main__':
    start_time = time.time()
    thread_count = 4

    chunk_size = len(urls) // thread_count
    url_chunks = [urls[i * chunk_size:(i + 1) * chunk_size] for i in range(thread_count)]

    if len(urls) % thread_count:
        url_chunks[-1].extend(urls[thread_count * chunk_size:])

    threads = []
    for chunk in url_chunks:
        thread = threading.Thread(target=process_urls, args=(chunk,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print(f"Total execution time: {time.time() - start_time:.2f} seconds")
