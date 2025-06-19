import multiprocessing
import time

def calculate_partial_sum(start, end):
    return sum(range(start, end))

def calculate_sum(n, num_processes=4):
    with multiprocessing.Pool(processes=num_processes) as pool:
        step = n // num_processes
        tasks = []

        for i in range(num_processes):
            start = i * step + 1
            end = (i + 1) * step + 1 if i != num_processes - 1 else n + 1
            tasks.append((start, end))

        results = pool.starmap(calculate_partial_sum, tasks)

    return sum(results)

if __name__ == "__main__":
    n = 1_000_000_000
    start_time = time.time()
    result = calculate_sum(n)
    end_time = time.time()
    print(f"Multiprocessing result: {result}")
    print(f"Execution time: {end_time - start_time:.2f} seconds")
