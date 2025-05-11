import asyncio
import time

async def partial_sum(start, end):
    return sum(range(start, end))

async def main():
    n = 1_000_000_000
    num_tasks = 10
    chunk_size = n // num_tasks

    start_time = time.time()

    tasks = []
    for i in range(0, n, chunk_size):
        start = i + 1
        end = min(i + chunk_size, n) + 1
        tasks.append(partial_sum(start, end))

    results = await asyncio.gather(*tasks)
    total = sum(results)

    end_time = time.time()
    print(f"Сумма: {total}, время: {end_time - start_time:.2f} сек")

asyncio.run(main())