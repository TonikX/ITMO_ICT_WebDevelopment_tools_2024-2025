import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

def calculate_partial_sum(start, end):
    return sum(range(start, end))

async def main():
    start_time = time.time()
    total = 10_000_000
    num_tasks = 4
    chunk_size = total // num_tasks

    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        tasks = [
            loop.run_in_executor(executor, calculate_partial_sum, i * chunk_size, (i + 1) * chunk_size if i != num_tasks - 1 else total)
            for i in range(num_tasks)
        ]
        results = await asyncio.gather(*tasks)

    total_sum = sum(results)
    print(f"Asyncio result: {total_sum}, Time: {time.time() - start_time:.2f} sec")

if __name__ == "__main__":
    asyncio.run(main())