import asyncio
import time

async def calculate_sum(start, end):
    return sum(range(start, end + 1))

async def main():
    N = 10_000_000_000
    NUM_TASKS = 4
    step = N // NUM_TASKS

    tasks = []
    for i in range(NUM_TASKS):
        start_range = i * step + 1
        end_range = (i + 1) * step if i < NUM_TASKS - 1 else N
        tasks.append(asyncio.create_task(calculate_sum(start_range, end_range)))

    t0 = time.time()
    results = await asyncio.gather(*tasks)
    total = sum(results)
    print("Asyncio result:", total)
    print("Time:", time.time() - t0, "seconds")

if __name__ == "__main__":
    asyncio.run(main())
