import asyncio
import multiprocessing
import threading
import time

limit = 10_000_000_000


def partial_sum_threading(start, end, result, index):
    result[index] = sum(range(start, end))


def calculate_sum_threading(n=10 ** 8, num_threads=16):
    step = n // num_threads
    result = [0] * num_threads
    threads = []

    for i in range(num_threads):
        print("starting thread", i)
        start = i * step + 1
        end = (i + 1) * step + 1 if i != num_threads - 1 else n + 1
        thread = threading.Thread(target=partial_sum_threading, args=(start, end, result, i))
        threads.append(thread)
        thread.start()

    print("all threads started")

    for thread in threads:
        print("gathered thread", thread)
        thread.join()

    return sum(result)


def partial_sum_multiprocessing(start, end):
    return sum(range(start, end))


def calculate_sum_multiprocessing(n=10 ** 8, num_processes=multiprocessing.cpu_count()):
    step = n // num_processes
    args = [(i * step + 1, (i + 1) * step + 1 if i != num_processes - 1 else n + 1)
            for i in range(num_processes)]

    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.starmap(partial_sum_multiprocessing, args)

    return sum(results)


async def partial_sum_async(start, end):
    return sum(range(start, end))


async def calculate_sum_async(n=10 ** 8, num_tasks=4):
    step = n // num_tasks
    tasks = [partial_sum_async(i * step + 1, (i + 1) * step + 1 if i != num_tasks - 1 else n + 1)
             for i in range(num_tasks)]
    results = await asyncio.gather(*tasks)
    return sum(results)


if __name__ == "__main__":
    start_time = time.time()
    total = calculate_sum_threading(limit)
    duration = time.time() - start_time
    print(f"[Threading] Сумма: {total}")
    print(f"[Threading] Время: {duration:.2f} сек")

    start_time = time.time()
    total = calculate_sum_multiprocessing(limit)
    duration = time.time() - start_time
    print(f"[Multiprocessing] Сумма: {total}")
    print(f"[Multiprocessing] Время: {duration:.2f} сек")

    start_time = time.time()
    total = asyncio.run(calculate_sum_async(limit))
    duration = time.time() - start_time
    print(f"[Asyncio] Сумма: {total}")
    print(f"[Asyncio] Время: {duration:.2f} сек")
