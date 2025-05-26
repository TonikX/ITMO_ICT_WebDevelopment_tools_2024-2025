import asyncio
import time

async def calculate_sum(start: int, end: int) -> int:
    total = 0
    for i in range(start, end + 1):
        total += i
    return total

async def main():
    N = 100_000_000
    num_tasks = 4
    chunk = N // num_tasks

    tasks = []
    for i in range(num_tasks):
        s = i * chunk + 1
        e = (i + 1) * chunk if i < num_tasks - 1 else N
        tasks.append(asyncio.create_task(calculate_sum(s, e)))

    t0 = time.time()
    results = await asyncio.gather(*tasks)
    total = sum(results)
    t1 = time.time()

    print(f"Asyncio: сумма = {total}, время = {t1 - t0:.3f} сек")

if __name__ == "__main__":
    asyncio.run(main())
