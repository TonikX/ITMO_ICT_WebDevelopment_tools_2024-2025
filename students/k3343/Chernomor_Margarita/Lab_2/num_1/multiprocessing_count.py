import multiprocessing
import time


def calculate_partial_sum(start, end):
    return sum(range(start, end))


def multiprocessing_sum():
    num_processes = 4
    total = 1000000000
    step = total // num_processes
    with multiprocessing.Pool(processes=num_processes) as pool:
        tasks = [(i * step, (i + 1) * step if i != num_processes - 1 else total) for i in range(num_processes)]
        results = pool.starmap(calculate_partial_sum, tasks)

    return sum(results)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    start_time = time.time()
    result = multiprocessing_sum()
    print("Multiprocessing result:", result)
    print("Execution time:", time.time() - start_time, "seconds")
