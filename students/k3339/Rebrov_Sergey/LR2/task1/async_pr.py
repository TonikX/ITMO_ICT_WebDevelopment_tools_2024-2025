import time
import asyncio


async def partial_sum(start, end):
    total = 0
    for i in range(start, end):
        total += i
        if i % 1000000 == 0:
            await asyncio.sleep(0)
    return total


async def calculate_sum(total=10 ** 9, num_parts=4):
    step = total // num_parts
    tasks = [
        partial_sum(i * step, total if i == num_parts - 1 else (i + 1) * step)
        for i in range(num_parts)
    ]
    results = await asyncio.gather(*tasks)
    return sum(results)


start_time = time.time()
print(f"Сумма: {asyncio.run(calculate_sum())}")
print(f"Время: {time.time() - start_time:.2f} сек")
