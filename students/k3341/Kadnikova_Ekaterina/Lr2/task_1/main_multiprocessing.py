import multiprocessing
import time

def calculate_partial_sum(start, end):
    return sum(range(start, end))

def main():
    start_time = time.time()
    num_processes = 4
    total = 10_000_000_000
    chunk_size = total // num_processes
    pool = multiprocessing.Pool(processes=num_processes)
    tasks = []

    for i in range(num_processes):
        start = i * chunk_size
        end = total if i == num_processes - 1 else (i + 1) * chunk_size
        tasks.append(pool.apply_async(calculate_partial_sum, (start, end)))

    results = [task.get() for task in tasks]
    total_sum = sum(results)
    print(f"Multiprocessing result: {total_sum}, Time: {time.time() - start_time:.2f} sec")

if __name__ == "__main__":
    main()