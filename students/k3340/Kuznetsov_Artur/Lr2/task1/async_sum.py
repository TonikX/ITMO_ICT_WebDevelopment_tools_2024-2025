import asyncio
import time


async def calculate_sum(start, end):
    return sum(range(start, end + 1))


async def main(N = 10 ** 9, num_parts = 4):
    start_time = time.time()

    chunk_size = N // num_parts
    ranges = []
    for i in range(num_parts):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_parts - 1 else N
        ranges.append((start, end))

    tasks = [calculate_sum(start, end) for start, end in ranges]
    results = await asyncio.gather(*tasks)

    total_sum = sum(results)
    end_time = time.time()

    print(f"Sum: {total_sum}")
    print(f"Time: {end_time - start_time:.2f} seconds")
