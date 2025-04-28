import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

def partial_sum(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
    return total

async def calculate_sum():
    total_start = 1
    total_end = 1_000_000_000
    num_tasks = 8
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
    start_time = time.time()
    total = asyncio.run(calculate_sum())
    end_time = time.time()
    print(f"sum: {total}")
    print(f"time: {end_time - start_time:.2f} seconds")
