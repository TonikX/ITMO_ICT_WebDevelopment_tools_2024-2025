import asyncio
import time


async def calculate_sum(a, b):
    s = 0
    for i in range(a, b + 1):
        s += i
    return s


async def main(n, count_of_tasks):
    start_time = time.time()
    size = n // count_of_tasks
    tasks = []
    for i in range(count_of_tasks):
        a = i * size + 1
        b = (i + 1) * size if (i + 1) * size < n else n
        task = asyncio.create_task(calculate_sum(a, b))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    total = sum(results)
    print("Result:", total)
    end_time = time.time()
    print("Total time:", end_time - start_time)


if __name__ == '__main__':
    asyncio.run(main(10 ** 9, 10))
