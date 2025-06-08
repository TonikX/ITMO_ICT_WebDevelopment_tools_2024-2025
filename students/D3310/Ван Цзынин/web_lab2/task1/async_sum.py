import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime


def calculate_partial_sum(start, end):
    return sum(range(start, end))

async def main():
    total = 10_000_000
    num_tasks = 4
    step = total // num_tasks
    ranges = [(i * step, total if i == num_tasks - 1 else (i + 1) * step) for i in range(num_tasks)]

    start_time = time.perf_counter()

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=num_tasks) as executor:
        tasks = [
            loop.run_in_executor(executor, calculate_partial_sum, start, end)
            for start, end in ranges
        ]
        results = await asyncio.gather(*tasks)

    total_sum = sum(results)
    elapsed = time.perf_counter() - start_time

    print(f"AsyncIO sum = {total_sum}")
    print(f"Time: {elapsed:.2f} seconds")

    with open('sum_timings.csv', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()},asyncio,{elapsed:.6f}\n")

if __name__ == "__main__":
    asyncio.run(main())