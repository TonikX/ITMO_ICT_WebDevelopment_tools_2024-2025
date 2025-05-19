import asyncio
import time
from typing import List

def calculate_partial_sum(start: int, end: int) -> int:
    return sum(range(start, end + 1))

async def calculate_sum(n: int = 10**9, num_tasks: int = 4) -> int:
    chunk = n // num_tasks
    loop = asyncio.get_event_loop()
    tasks: List[asyncio.Future] = []

    for i in range(num_tasks):
        start = i * chunk + 1
        end = (i + 1) * chunk if i < num_tasks - 1 else n
        tasks.append(loop.run_in_executor(None, calculate_partial_sum, start, end))

    partial_results = await asyncio.gather(*tasks)
    return sum(partial_results)

async def main():
    t0 = time.perf_counter()
    total = await calculate_sum(n=10**9, num_tasks=4)
    elapsed = time.perf_counter() - t0
    print(f"Total sum: {total}")
    print(f"Elapsed time (asyncio): {elapsed:.6f} seconds")
