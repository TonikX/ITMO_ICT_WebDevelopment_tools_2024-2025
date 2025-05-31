import multiprocessing
import time

def calculate_sum(start, end):
    return sum(range(start, end + 1))

if __name__ == '__main__':
    N = 5000000000
    num_processes = 4
    chunk_size = N // num_processes
    ranges = []
    for i in range(num_processes):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_processes - 1 else N
        ranges.append((start, end))

    start_time = time.time()
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.starmap(calculate_sum, ranges)

    total = sum(results)
    end_time = time.time()

    print(f"Multiprocessing Total: {total}")
    print(f"Multiprocessing Time: {end_time - start_time:.2f} seconds")