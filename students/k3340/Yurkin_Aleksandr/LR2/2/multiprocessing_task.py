import multiprocessing
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

def worker(url_list: list[str]):
    for url in url_list:
        try:
            parse_and_save(url)
            print(f"[Process] {url} parsed and saved")
        except Exception as e:
            print(f"[Process] Error {url}: {e}")

if __name__ == '__main__':
    start = time.time()
    num_processes = 4
    chunk_size = len(urls) // num_processes
    chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]

    processes = []
    for chunk in chunks:
        process = multiprocessing.Process(target=worker, args=(chunk,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    print(f"Multiprocessing total time: {time.time() - start:.2f}s")
