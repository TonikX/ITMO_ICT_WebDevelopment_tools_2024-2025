import asyncio
import time

N = 1_000_000_000
TASKS = 4

async def calculate_sum(start, end):
    return sum(range(start, end))

async def run_async():
    step = N // TASKS
    start_time = time.time()

    tasks = [
        asyncio.create_task(calculate_sum(i * step, N if i == TASKS - 1 else (i + 1) * step))
        for i in range(TASKS)
    ]
    results = await asyncio.gather(*tasks)
    total = sum(results)
    print("Async Total:", total)
    print("Async Time:", time.time() - start_time)
if __name__ == "__main__":
    asyncio.run(run_async())
