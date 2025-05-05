import asyncio
import time


async def calculate_sum(start, end):
    local_sum = 0
    for i in range(start, end + 1):
        local_sum += i
        if i % 1_000_000 == 0:
           await asyncio.sleep(0)
    return local_sum


async def main():
    TOTAL_SUM_UP_TO = 100_000_000
    NUM_TASKS = 4

    chunk_size = TOTAL_SUM_UP_TO // NUM_TASKS
    tasks = []
    for i in range(NUM_TASKS):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < NUM_TASKS - 1 else TOTAL_SUM_UP_TO
        task = asyncio.create_task(calculate_sum(start, end))
        tasks.append(task)

    start_time = time.perf_counter()

    partial_sums = await asyncio.gather(*tasks)

    total_sum = sum(partial_sums)

    end_time = time.perf_counter()

    print(f"Asyncio:")
    print(f"Calculated sum: {total_sum}")
    print(f"Execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main()) 