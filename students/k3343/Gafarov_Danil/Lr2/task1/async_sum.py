import asyncio
import time

TOTAL = 1_000_000_000
TASKS = 4

async def calculate_sum(start, end):
    partial_sum = 0
    for i in range(start, end + 1):
        partial_sum += i
    return partial_sum

async def main():
    step = TOTAL // TASKS
    tasks = []

    start_time = time.time()

    for i in range(TASKS):
        start = i * step + 1
        end = (i + 1) * step if i != TASKS - 1 else TOTAL
        task = asyncio.create_task(calculate_sum(start, end))
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    total_sum = sum(results)
    end_time = time.time()

    print(f"Asyncio: Сумма = {total_sum}, время = {end_time - start_time:.4f} сек")

if __name__ == "__main__":
    asyncio.run(main())