import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

N = 1_000_000_000
THREADS = 4

def calculate_sum(start, end):
    return sum(range(start, end))

async def main():
    start_time = time.time()
    loop = asyncio.get_running_loop()
    step = N // THREADS
    with ThreadPoolExecutor() as executor:
        tasks = [
            loop.run_in_executor(executor, calculate_sum, i * step, N if i == THREADS - 1 else (i + 1) * step)
            for i in range(THREADS)
        ]
        results = await asyncio.gather(*tasks)
    total = sum(results)
    print("Asyncio Result:", total)
    print("Time:", time.time() - start_time)

if __name__ == "__main__":
    asyncio.run(main())
