import multiprocessing
import time
from parser import parse_and_save

urls = [f'https://timus.online/problem.aspx?space=1&num={i}' for i in range(1000, 1100)]


def process_urls(urls):
    for url in urls:
        parse_and_save(url)


if __name__ == '__main__':
    start = time.time()
    num_processes = 4
    chunk_size = len(urls) // num_processes
    chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]

    processes = []
    for chunk in chunks:
        process = multiprocessing.Process(target=process_urls, args=(chunk,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    print(f"Total execution time: {time.time() - start:.2f} seconds")
