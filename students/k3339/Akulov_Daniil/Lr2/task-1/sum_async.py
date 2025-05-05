import time
import asyncio


async def calculate_sum(start, end):
    return sum(range(start, end))


async def main():
    num_tasks = 4
    chunk_size = 10_000_000 // num_tasks
    tasks = []
    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size + 1
        task = asyncio.create_task(calculate_sum(start, end))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    total_sum = sum(results)
    print("Async sum:", total_sum)


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Time (sec): {end_time - start_time:.6f}")