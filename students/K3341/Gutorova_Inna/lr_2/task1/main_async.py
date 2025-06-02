import asyncio
import time


async def calculate_sum(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


async def async_sum():
    num_tasks = 4
    total_numbers = 10 ** 6  # Уменьшено для демонстрации
    chunk_size = total_numbers // num_tasks
    tasks = []

    start_time = time.time()

    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_tasks - 1 else total_numbers
        tasks.append(asyncio.create_task(calculate_sum(start, end)))

    results = await asyncio.gather(*tasks)
    total_sum = sum(results)
    end_time = time.time()

    print(f"Async sum: {total_sum}, Time: {end_time - start_time:.4f} seconds")


asyncio.run(async_sum())