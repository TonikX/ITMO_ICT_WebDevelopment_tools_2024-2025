import multiprocessing
import time
from typing import Tuple, List

def calculate_partial_sum(args: Tuple[int, int]) -> int:
    start, end = args
    return sum(range(start, end + 1))

def calculate_sum(n: int = 10**9, num_processes: int = 4) -> int:
    chunk = n // num_processes
    ranges: List[Tuple[int, int]] = []
    for i in range(num_processes):
        start = i * chunk + 1
        end = (i + 1) * chunk if i < num_processes - 1 else n
        ranges.append((start, end))

    with multiprocessing.Pool(processes=num_processes) as pool:
        partial_results = pool.map(calculate_partial_sum, ranges)

    return sum(partial_results)

def main():
    t0 = time.perf_counter()
    total = calculate_sum(n=10**9, num_processes=4)
    elapsed = time.perf_counter() - t0
    print(f"Total sum: {total}")
    print(f"Elapsed time (multiprocessing): {elapsed:.6f} seconds")
