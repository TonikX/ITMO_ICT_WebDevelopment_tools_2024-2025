import multiprocessing
import time
from datetime import datetime


def calculate_partial_sum(start, end):
    return sum(range(start, end))

def main():
    total = 10_000_000
    num_processes = 4
    step = total // num_processes
    ranges = []

    for i in range(num_processes):
        a = i * step
        b = total if i == num_processes - 1 else (i + 1) * step
        ranges.append((a, b))

    start_time = time.perf_counter()

    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.starmap(calculate_partial_sum, ranges)

    total_sum = sum(results)
    elapsed = time.perf_counter() - start_time

    print(f"Multiprocessing sum = {total_sum}")
    print(f"Time: {elapsed:.2f} seconds")

    with open('sum_timings.csv', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()},multiprocessing,{elapsed:.6f}\n")

if __name__ == "__main__":
    multiprocessing.set_start_method("fork")
    main()