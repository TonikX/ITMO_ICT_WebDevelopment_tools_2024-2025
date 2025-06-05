import multiprocessing
import time


def partial_sum(start, end, result, index):
    result[index] = sum(range(start, end))

def calculate_sum():
    num_processes = multiprocessing.cpu_count()
    maximum = 10**9
    step = maximum // num_processes
    manager = multiprocessing.Manager()
    processes = []
    results = manager.list([0] * num_processes)
    for i in range(num_processes):
        start = i * step + 1
        if i != num_processes - 1:
            end = (i + 1) * step + 1
        else:
            end = maximum + 1
        process = multiprocessing.Process(target=partial_sum, args=(start, end, results, i))
        processes.append(process)
        process.start()
    for process in processes:
        process.join()
    return sum(results)


if __name__ == "__main__":
    start_time = time.time()
    total = calculate_sum()
    duration = time.time() - start_time
    print("Итоговая сумма:", total)
    print("Время выполнения:", time.time() - start_time, "сек")

