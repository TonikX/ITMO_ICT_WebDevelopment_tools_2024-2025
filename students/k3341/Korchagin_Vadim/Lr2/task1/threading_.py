import threading
import time
from typing import List

def calculate_partial_sum(start: int, end: int, results: List[int], index: int) -> None:
    results[index] = sum(range(start, end + 1))

def calculate_sum(n: int = 10**9, num_threads: int = 4) -> int:
    chunk = n // num_threads
    threads: List[threading.Thread] = []
    results: List[int] = [0] * num_threads

    for i in range(num_threads):
        start = i * chunk + 1
        end = (i + 1) * chunk if i < num_threads - 1 else n
        t = threading.Thread(
            target=calculate_partial_sum,
            args=(start, end, results, i)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return sum(results)

def main():
    t0 = time.perf_counter()
    total = calculate_sum(n=10**9, num_threads=4)
    elapsed = time.perf_counter() - t0
    print(f"Total sum: {total}")
    print(f"Elapsed time (threading): {elapsed:.6f} seconds")
