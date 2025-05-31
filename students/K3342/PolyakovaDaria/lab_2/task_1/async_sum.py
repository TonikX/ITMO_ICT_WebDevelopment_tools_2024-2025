import asyncio
import time


async def calculate_sum(start, end):
    return sum(range(start, end))


async def main():
    total = 10_000_000
    num_tasks = 4
    step = total // num_tasks

    start_time = time.time()

    tasks = []
    for i in range(num_tasks):
        start_i = i * step
        end_i = (i + 1) * step
        tasks.append(asyncio.create_task(calculate_sum(start_i, end_i)))

    results = await asyncio.gather(*tasks)
    total_sum = sum(results)

    print(f"Async sum: {total_sum}")
    print(f"Execution time: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
