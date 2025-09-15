import time
import asyncio

def calculate_partial_sum(start, end):
    return end * (end + 1) // 2 - (start - 1) * start // 2

async def async_calculate_partial_sum(start, end):
    return calculate_partial_sum(start, end)

N = 10000000000000
NUM_TASKS = 4
chunk_size = N // NUM_TASKS

async def main():
    start_time = time.time()

    tasks = []
    for i in range(NUM_TASKS):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < NUM_TASKS - 1 else N
        task = async_calculate_partial_sum(start, end)
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    total_sum = sum(results)

    end_time = time.time()
    print(f"Async sum: {total_sum}")
    print(f"Async time: {end_time - start_time} seconds")

asyncio.run(main())