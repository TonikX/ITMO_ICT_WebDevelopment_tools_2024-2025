import time
import asyncio

async def calculate_sum():
    from_value = 1
    to_value = 10**9
    workers_count = 32
    tasks = []
    step = (to_value - from_value) // workers_count
    result = [0] * workers_count

    for i in range(workers_count):
        start = from_value + i * step
        end = from_value + (i + 1) * step
        tasks.append(calculate_worker(start, end, result, i))

    await asyncio.gather(*tasks)
    return sum(result) + sum(range(from_value + workers_count * step, to_value + 1))

async def calculate_worker(start, end, result, index):
    total = sum(range(start, end))
    result[index] = total


start_time = time.perf_counter()
sum_result = asyncio.run(calculate_sum())
end_time = time.perf_counter()
print(sum_result)
print(f"{end_time - start_time} seconds")