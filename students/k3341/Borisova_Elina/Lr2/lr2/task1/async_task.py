import asyncio
import time

async def calculate_sum(start, end):
    return sum(range(start, end + 1))

async def main():
    total = 1000_000_000
    tasks_num = 4
    chunk_size = total // tasks_num
    tasks = []

    start_time = time.time()

    for i in range(tasks_num):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != tasks_num - 1 else total
        tasks.append(asyncio.create_task(calculate_sum(start, end)))

    results = await asyncio.gather(*tasks)
    total_sum = sum(results)
    end_time = time.time()

    print(f"Async sum: {total_sum}")
    print(f"Time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())