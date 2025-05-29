import asyncio
import time


async def calculate_sum(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


async def async_sum(N, num_tasks=4):
    chunk_size = N // num_tasks
    tasks = []

    start_time = time.time()

    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_tasks - 1 else N
        tasks.append(calculate_sum(start, end))

    results = await asyncio.gather(*tasks)
    total = sum(results)

    end_time = time.time()
    print(f"Async sum: {total}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    N = 1_000_000_000
    asyncio.run(async_sum(N))

# first tray Async sum: 500000000500000000
# Time taken: 29.7306 seconds

# second tray Async sum: 500000000500000000
# Time taken: 28.7105 seconds
