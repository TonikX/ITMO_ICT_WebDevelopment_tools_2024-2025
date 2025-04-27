import asyncio
import time

N = 10**9
PARTS = 5


async def calculate_range(start: int, end: int) -> int:
    return sum(range(start, end))


async def calculate_sum_asyncio() -> int:
    chunk_size = N // PARTS
    tasks = []
    for i in range(PARTS):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size + 1
        tasks.append(calculate_range(start, end))

    t0 = time.time()
    results = await asyncio.gather(*tasks)
    t1 = time.time()
    result_asyncio = sum(results)
    print(f"Asyncio result: {result_asyncio}, time: {t1 - t0:.2f}s")


if __name__ == "__main__":
    asyncio.run(calculate_sum_asyncio())