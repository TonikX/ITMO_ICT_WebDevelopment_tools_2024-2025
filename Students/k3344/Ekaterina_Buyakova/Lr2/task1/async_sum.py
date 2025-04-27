import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

def calculate_sum_of_range(start, end):
    total = 0
    for number in range(start, end):
        total += number
    return total

async def calculate_sum(limit, num_tasks):
    print(f"Вычисляем сумму от 1 до {limit} с помощью {num_tasks} async-задач...")

    start_time = time.time()
    chunk_size = limit // num_tasks

    ranges = [
        (i * chunk_size + 1, (i + 1) * chunk_size + 1 if i != num_tasks - 1 else limit + 1)
        for i in range(num_tasks)
    ]

    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=num_tasks) as executor:
        tasks = [
            loop.run_in_executor(executor, calculate_sum_of_range, start, end)
            for start, end in ranges
        ]
        results = await asyncio.gather(*tasks)

    total_sum = sum(results)
    end_time = time.time()

    print(f"Сумма: {total_sum}")
    print(f"Async-задачи: {num_tasks}")
    print(f"Время выполнения: {end_time - start_time:.3f} секунд")

if __name__ == "__main__":
    limit = 1000000000
    for threads in range(4, 5):
        asyncio.run(calculate_sum(limit, threads))
