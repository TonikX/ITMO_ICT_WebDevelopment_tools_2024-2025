import asyncio
import time

async def partial_sum(start, end):
    return sum(range(start, end))

async def calculate_sum():
    n = 1_000_000_000
    num_tasks = 4
    step = n // num_tasks

    tasks = []
    for i in range(num_tasks):
        start = i * step
        end = n if i == num_tasks - 1 else (i + 1) * step
        tasks.append(partial_sum(start, end))

    results = await asyncio.gather(*tasks)
    return sum(results)
