import threading
import time
from parse_and_save import parse_and_save

urls = [
    "https://sletat.ru/tours/turkey/",
    "https://sletat.ru/tours/uae/",
    "https://sletat.ru/tours/egypt/",
    "https://sletat.ru/tours/vietnam/",
    "https://sletat.ru/tours/thailand/",
    "https://sletat.ru/tours/maldives/",
    "https://sletat.ru/tours/russia/",
    "https://sletat.ru/tours/cuba/",
    "https://sletat.ru/tours/sri_lanka/",
    "https://sletat.ru/tours/china/",
    "https://sletat.ru/tours/abkhazia/",
]

def worker(url_list):
    for url in url_list:
        try:
            parse_and_save(url)
            print(f"[Thread] {url} parsed and saved")
        except Exception as e:
            print(f"[Thread] Error {url}: {e}")

if __name__ == '__main__':
    start = time.time()
    num_threads = 4

    chunk_size = len(urls) // num_threads
    chunks = [ urls[i*chunk_size : (i+1)*chunk_size] for i in range(num_threads) ]

    if len(urls) % num_threads:
        chunks[-1].extend(urls[num_threads*chunk_size:])

    threads = []
    for chunk in chunks:
        t = threading.Thread(target=worker, args=(chunk,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print(f"Threading total time: {time.time() - start:.2f}s")
