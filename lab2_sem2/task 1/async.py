import asyncio
import time


async def partial_sum(start, end):
    return sum(range(start, end))


async def calculate_sum(n, num_tasks):
    step = n // num_tasks
    tasks = []

    for i in range(num_tasks):
        start = i * step + 1  
        end = n + 1 if i == num_tasks - 1 else (i + 1) * step + 1
        tasks.append(asyncio.create_task(partial_sum(start, end)))

    results = await asyncio.gather(*tasks)
    return sum(results)


if __name__ == "__main__":
    n = 10 ** 9
    start_time = time.time()
    result = asyncio.run(calculate_sum(n, 5))
    print("Сумма:", result)
    print("Время выполнения:", time.time() - start_time, "сек")
