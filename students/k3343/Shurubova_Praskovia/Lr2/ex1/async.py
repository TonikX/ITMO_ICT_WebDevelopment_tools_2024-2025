import asyncio
import time

TOTAL = 1000000000
NUM_TASKS = 4


async def calculate_sum(start, end):
    total = 0
    for i in range(start, end):
        total += i
    return total


async def main():
    chunk = TOTAL // NUM_TASKS
    tasks = []

    start_time = time.time()
    for i in range(NUM_TASKS):
        start = i * chunk + 1
        end = (i + 1) * chunk + 1 if i != NUM_TASKS - 1 else TOTAL + 1
        tasks.append(asyncio.create_task(calculate_sum(start, end)))

    results = await asyncio.gather(*tasks)
    total_sum = sum(results)
    print("Total:", total_sum)
    print("Time (asyncio):", time.time() - start_time)

if __name__ == "__main__":
    asyncio.run(main())

# Time (asyncio): 41.82617259025574