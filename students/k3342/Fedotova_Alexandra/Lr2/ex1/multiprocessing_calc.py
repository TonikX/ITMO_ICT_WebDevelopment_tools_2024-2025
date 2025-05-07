import multiprocessing
import time

def partial_sum(start, end):
    return sum(range(start, end))

def calculate_sum():
    num_processes = 4
    n = 1_000_000_000
    step = n // num_processes
    pool = multiprocessing.Pool(processes=num_processes)

    tasks = [(i * step, n if i == num_processes - 1 else (i + 1) * step) for i in range(num_processes)]
    results = pool.starmap(partial_sum, tasks)
    pool.close()
    pool.join()
    return sum(results)