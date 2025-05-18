import multiprocessing as mp
import time

def calculate_sum(start: int, end: int) -> int:
    return (end - start + 1) * (start + end) // 2

def perform_task(params):
    return calculate_sum(*params)

if __name__ == "__main__":
    upper_limit = 10_000_000_000_000
    workers = mp.cpu_count()
    portion = upper_limit // workers

    ranges = []
    for idx in range(workers):
        from_val = idx * portion + 1
        to_val = (idx + 1) * portion if idx != workers - 1 else upper_limit
        ranges.append((from_val, to_val))

    start_time = time.perf_counter()
    with mp.Pool(processes=workers) as executor:
        output = executor.map(perform_task, ranges)
    final_sum = sum(output)
    end_time = time.perf_counter()

    print(f"Multiprocessing: result = {final_sum}, duration = {end_time - start_time:.6f} seconds")