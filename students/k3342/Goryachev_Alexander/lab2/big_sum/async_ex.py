import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

MAX_NUMBER = 1_000_000_000
NUM_TASKS = 10

def blocking_sum(start, end):
    return sum(range(start, end + 1))

async def async_partial_sum(executor, start, end):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, blocking_sum, start, end)

async def calculate_sum():
    step = MAX_NUMBER // NUM_TASKS
    ranges = []

    for i in range(NUM_TASKS):
        start = i * step + 1
        end = (i + 1) * step if i < NUM_TASKS - 1 else MAX_NUMBER
        ranges.append((start, end))

    results = []
    with ThreadPoolExecutor(max_workers=NUM_TASKS) as executor:
        tasks = [
            async_partial_sum(executor, start, end)
            for start, end in ranges
        ]
        results = await asyncio.gather(*tasks)

    return sum(results)

if __name__ == "__main__":
    start_time = time.time()
    result = asyncio.run(calculate_sum())
    end_time = time.time()

    print(f"Сумма от 1 до {MAX_NUMBER}: {result}")
    print(f"Время выполнения: {end_time - start_time:.2f} секунд")