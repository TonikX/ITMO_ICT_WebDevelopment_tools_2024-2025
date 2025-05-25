import time
import asyncio

MAX_VALUE = 10**9
WORKERS = 100

async def partial_sum(start, step):
    return sum(range(start, MAX_VALUE, step))

async def calculate_sum():
    jobs  = [partial_sum(i, WORKERS) for i in range(WORKERS)]
    return await asyncio.gather(*jobs )

if __name__ == '__main__':
    start = time.time()
    sums = asyncio.run(calculate_sum())
    duration = time.time() - start
    print(f"Итоговая сумма:", sum(sums))
    print(f"Затрачено времени: {duration:.3f} сек")