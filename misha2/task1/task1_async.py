import asyncio
import time

TOTAL = 100_000_000
NUM_WORKERS = 4

async def calculate_sum(start, end):
    return await asyncio.to_thread(sum, range(start, end + 1))

async def main():
    step = TOTAL // NUM_WORKERS
    tasks = []

    start_time = time.time()

    for i in range(NUM_WORKERS):
        start = i * step + 1
        end = (i + 1) * step if i != NUM_WORKERS - 1 else TOTAL
        tasks.append(calculate_sum(start, end))

    results = await asyncio.gather(*tasks)

    total = sum(results)
    duration = time.time() - start_time

    print(f"Async total sum: {total}")
    print(f"Async duration: {duration:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())