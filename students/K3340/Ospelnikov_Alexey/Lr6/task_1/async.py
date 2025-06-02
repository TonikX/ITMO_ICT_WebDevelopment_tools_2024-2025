import asyncio
import time

n = int(1e9)

async def counter(begin, shift):
    return sum(range(begin, n, shift))

async def calculate_sum():
    coroutines_count = 100
    tasks = [counter(i, coroutines_count) for i in range(coroutines_count)]
    return await asyncio.gather(*tasks)

if __name__ == '__main__':
    start = time.time()
    sums = asyncio.run(calculate_sum())
    print("Сумма:", sum(sums), "Время:", time.time() - start)