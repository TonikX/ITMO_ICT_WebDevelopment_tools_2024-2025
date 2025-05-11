import multiprocessing
import os
import time


def partial_sum(start, end, res_queue):
    total = sum(range(start, end))
    res_queue.put(total)


def main():
    n = 1_000_000_000
    num_processes = 4
    chunk_size = n // num_processes

    res_queue = multiprocessing.Queue()
    processes = []

    start_time = time.time()

    for i in range(num_processes):
        start = i * chunk_size + 1
        if i == num_processes - 1:
            end = n + 1
        else:
            end = start + chunk_size

        p = multiprocessing.Process(
            target=partial_sum,
            args=(start, end, res_queue)
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    results = []
    while not res_queue.empty():
        results.append(res_queue.get())

    total = sum(results)
    end_time = time.time()

    print(f"Сумма: {total}, время: {end_time - start_time:.2f} сек")


if __name__ == '__main__':
    main()
