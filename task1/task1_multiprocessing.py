# multiprocessing_sum.py
from multiprocessing import Process, Array
import time
import os

TOTAL = 10_000_000_000
NUM_WORKERS = os.cpu_count() or 4

def calculate_sum(start, end, index, results):
    results[index] = sum(range(start, end + 1))

def main():
    step = TOTAL // NUM_WORKERS
    results = Array('Q', NUM_WORKERS)
    processes = []

    start_time = time.time()

    for i in range(NUM_WORKERS):
        start = i * step + 1
        end = (i + 1) * step if i != NUM_WORKERS - 1 else TOTAL
        p = Process(target=calculate_sum, args=(start, end, i, results))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    total = sum(results)
    duration = time.time() - start_time

    print(f"Multiprocessing total sum: {total}")
    print(f"Multiprocessing duration: {duration:.2f} seconds")

if __name__ == "__main__":
    main()
