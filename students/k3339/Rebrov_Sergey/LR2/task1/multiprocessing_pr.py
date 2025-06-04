import time
import multiprocessing


def partial_sum(start, end):
    return sum(range(start, end))


def calculate_sum(total=10 ** 9, num_processes=32):
    step = total // num_processes
    with multiprocessing.Pool(processes=num_processes) as pool:
        tasks = [(i * step, total if i == num_processes - 1 else (i + 1) * step) for i in range(num_processes)]
        results = pool.starmap(partial_sum, tasks)
    return sum(results)


if __name__ == "__main__":
    start_time = time.time()
    print(f"Сумма: {calculate_sum()}")
    print(f"Время: {time.time() - start_time:.2f} сек")
