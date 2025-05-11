import asyncio
import time


async def partial_sum(start, end):
    return sum(range(start, end))


async def calculate_sum():
    num_tasks = 4
    maximum = 10**9
    step = maximum // num_tasks
    tasks = []

    for i in range(num_tasks):
        start = i * step + 1
        if i != num_tasks - 1:
            end = (i + 1) * step + 1
        else:
            end = maximum + 1
        task = asyncio.create_task(partial_sum(start, end))
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return sum(results)

if __name__ == "__main__":
    start_time = time.time()
    total = asyncio.run(calculate_sum())
    duration = time.time() - start_time
    print("Asyncio")
    print("Итоговая сумма:", total)
    print("Время выполнения:", time.time() - start_time, "сек")
