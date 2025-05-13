import asyncio, time
from concurrent.futures import ProcessPoolExecutor

n = 10**13
k = 4

def sum_range(start: int, end: int) -> int:
    """
    Подсчитывает сумму чисел в диапазоне [start, end]
    :param start: начало диапазона
    :param end: конец диапазона
    :return: сумму чисел на заданном отрезке
    """
    s = 0
    for i in range(start, end + 1):
        s += i
    return s

async def calculate_sum():
    chunk = n // k
    loop = asyncio.get_running_loop()
    tasks = []
    start_time = time.perf_counter()

    with ProcessPoolExecutor(max_workers=k) as executor:
        for i in range(k):
            a = i * chunk + 1
            b = (i + 1) * chunk if i < k - 1 else n
            tasks.append(loop.run_in_executor(executor, sum_range, a, b))
        results = await asyncio.gather(*tasks)

    s = sum(results)
    elapsed = time.perf_counter() - start_time
    print(f"[asyncio] sum = {s}, time = {elapsed:.2f}s")

if __name__ == "__main__":
    asyncio.run(calculate_sum())
