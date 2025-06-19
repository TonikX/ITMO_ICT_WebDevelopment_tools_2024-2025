import asyncio
import time

async def calculate_partial_sum(start, end):
    return sum(range(start, end))

async def calculate_sum(n, num_tasks=4):
    step = n // num_tasks
    tasks = []

    for i in range(num_tasks):
        start = i * step + 1
        end = (i + 1) * step + 1 if i != num_tasks - 1 else n + 1
        tasks.append(asyncio.create_task(calculate_partial_sum(start, end)))

    results = await asyncio.gather(*tasks)
    return sum(results)

if __name__ == "__main__":
    n = 1_000_000_000
    start_time = time.time()
    result = asyncio.run(calculate_sum(n))
    end_time = time.time()
    print(f"Asyncio result: {result}")
    print(f"Execution time: {end_time - start_time:.2f} seconds")