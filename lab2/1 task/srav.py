import threading
import multiprocessing
import asyncio
import time


# Threading версия
def calculate_sum_thread(start, end, results, index):
    total = 0
    for i in range(start, end + 1):
        total += i
    results[index] = total


def test_threading():
    print("Threading:")
    start_time = time.time()

    n = 10 ** 9
    num_threads = 8
    chunk_size = n // num_threads

    results = [0] * num_threads
    threads = []

    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_threads - 1 else n
        thread = threading.Thread(target=calculate_sum_thread, args=(start, end, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(results)
    end_time = time.time()

    print(f"Сумма: {total_sum}")
    print(f"Время: {end_time - start_time:.2f} секунд")
    print(f"Количество потоков: {num_threads}\n")


# Multiprocessing версия
def calculate_sum_process(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


def test_multiprocessing():
    print("Multiprocessing:")
    start_time = time.time()

    n = 10 ** 9
    num_processes = multiprocessing.cpu_count()
    chunk_size = n // num_processes

    tasks = []
    for i in range(num_processes):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_processes - 1 else n
        tasks.append((start, end))

    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.starmap(calculate_sum_process, tasks)

    total_sum = sum(results)
    end_time = time.time()

    print(f"Сумма: {total_sum}")
    print(f"Время: {end_time - start_time:.2f} секунд")
    print(f"Количество процессов: {num_processes}\n")


# Async версия
async def calculate_sum_async(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


async def test_async():
    print("Async:")
    start_time = time.time()

    n = 10 ** 9
    num_tasks = 8
    chunk_size = n // num_tasks

    tasks = []
    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_tasks - 1 else n
        tasks.append(calculate_sum_async(start, end))

    results = await asyncio.gather(*tasks)

    total_sum = sum(results)
    end_time = time.time()

    print(f"Сумма: {total_sum}")
    print(f"Время: {end_time - start_time:.2f} секунд")
    print(f"Количество задач: {num_tasks}\n")


def main():
    test_threading()
    test_multiprocessing()
    asyncio.run(test_async())


if __name__ == "__main__":
    main()