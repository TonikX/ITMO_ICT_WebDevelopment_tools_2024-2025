import asyncio
import time

async def calculate_partial_sum(start, end):
    return sum(range(start, end))

async def main():
    total = 10**8
    num_tasks = 4
    step = total // num_tasks
    tasks = []

    for i in range(num_tasks):
        start_range = i * step
        end_range = (i + 1) * step if i != num_tasks - 1 else total
        tasks.append(calculate_partial_sum(start_range, end_range))

    start_time = time.time()
    results = await asyncio.gather(*tasks)
    total_sum = sum(results)
    print(f"Total Sum: {total_sum}")
    print(f"Time taken with asyncio: {time.time() - start_time} seconds")

if __name__ == "__main__":
    asyncio.run(main())