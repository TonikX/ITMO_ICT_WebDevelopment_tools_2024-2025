import asyncio
import time
from concurrent.futures import ThreadPoolExecutor


def calculate_partial_sum(start, end):
    return sum(range(start, end))


async def async_sum():
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=4)
    total = 1000000000
    step = total // 4

    tasks = [
        loop.run_in_executor(executor, calculate_partial_sum, i * step, (i + 1) * step if i != 3 else total)
        for i in range(4)
    ]
    results = await asyncio.gather(*tasks)
    return sum(results)

start_time = time.time()
result = asyncio.run(async_sum())
print("Asyncio result:", result)
print("Execution time:", time.time() - start_time, "seconds")
