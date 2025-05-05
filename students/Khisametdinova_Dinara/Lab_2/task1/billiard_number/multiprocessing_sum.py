import multiprocessing
import time

def calculate_sum(start, end):
    return sum(range(start, end + 1))

def main(N = 1_000_000_000, num_parts = 4):
    start_time = time.time()
    pool = multiprocessing.Pool(processes = num_parts)

    chunk_size = N // num_parts
    ranges = []
    for i in range(num_parts):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_parts - 1 else N
        ranges.append((start, end))

    results = pool.starmap(calculate_sum, ranges)
    pool.close()
    pool.join()

    total_sum = sum(results)
    end_time = time.time()

    print(f"Sum: {total_sum}")
    print(f"Time: {end_time - start_time:.2f} seconds")

