import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

def partial_sum(start, end):
    n = end - start + 1
    return (start + end) * n // 2

async def calculate_sum(num_tasks):
    total_start = 1
    total_end = 10_000_000_000_000
    step = (total_end - total_start + 1) // num_tasks

    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        tasks = []
        for i in range(num_tasks):
            start = total_start + i * step
            end = start + step - 1 if i != num_tasks - 1 else total_end
            tasks.append(loop.run_in_executor(executor, partial_sum, start, end))
        results = await asyncio.gather(*tasks)

    return sum(results)

if __name__ == "__main__":
    for num_tasks in [4, 8, 12, 16, 24, 32]:
        start_time = time.time()
        total = asyncio.run(calculate_sum(num_tasks))
        end_time = time.time()
        print(f"Tasks: {num_tasks}, Time: {end_time - start_time:.2f} seconds")
