import multiprocessing
import time

def calculate_partial_sum(start, end):
    return sum(range(start, end))

def main():
    total = 10**8
    num_processes = 4
    step = total // num_processes
    pool = multiprocessing.Pool(processes=num_processes)
    tasks = []

    for i in range(num_processes):
        start_range = i * step
        end_range = (i + 1) * step if i != num_processes - 1 else total
        tasks.append((start_range, end_range))

    start_time = time.time()
    results = pool.starmap(calculate_partial_sum, tasks)
    total_sum = sum(results)
    print(f"Total Sum: {total_sum}")
    print(f"Time taken with multiprocessing: {time.time() - start_time} seconds")

if __name__ == "__main__":
    main()