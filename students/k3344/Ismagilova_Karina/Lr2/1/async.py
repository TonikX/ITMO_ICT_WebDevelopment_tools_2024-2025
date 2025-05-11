import asyncio
import time

async def calculate_partial_sum(start, end):
    return sum(range(start, end))

async def main():
    start_time = time.time()
    n_tasks = 4
    total = 1000000000
    chunk_size = total // n_tasks
    tasks = [calculate_partial_sum(i * chunk_size + 1, (i + 1) * chunk_size + 1) for i in range(n_tasks)]

    results = await asyncio.gather(*tasks)
    total_sum = sum(results)
    print("Total sum:", total_sum)
    print("Time:", time.time() - start_time)
    # Time: 30.117953777313232

if __name__ == "__main__":
    asyncio.run(main())
