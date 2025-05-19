import asyncio
import time

async def calculate_sum(start, end):
    return sum(range(start, end))

async def main():
    total = 1_000_000_000
    num_tasks = 4
    step = total // num_tasks

    tasks = [
        asyncio.create_task(calculate_sum(i * step + 1, (i * step + 1) + step))
        for i in range(num_tasks)
    ]

    results = await asyncio.gather(*tasks)
    print(f"Total sum: {sum(results)}")

start_time = time.time()
asyncio.run(main())
print(f"Execution time (asyncio): {time.time() - start_time:.2f} seconds")
