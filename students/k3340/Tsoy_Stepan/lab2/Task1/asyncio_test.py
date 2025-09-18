import asyncio
import time

N = 10**9
NUM_WORKERS = 4

async def calculate_sum(start, end):
    # CPU-bound код, поэтому придется использовать run_in_executor
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, sync_sum, start, end)

def sync_sum(start, end):
    s = 0
    for i in range(start, end + 1):
        s += i
    return s

async def main():
    step = N // NUM_WORKERS
    tasks = []
    for i in range(NUM_WORKERS):
        start = i * step + 1
        end = (i + 1) * step if i < NUM_WORKERS - 1 else N
        tasks.append(calculate_sum(start, end))

    t0 = time.time()
    results = await asyncio.gather(*tasks)
    total = sum(results)
    print("Async total:", total)
    print("Elapsed:", time.time() - t0, "sec")

if __name__ == "__main__":
    asyncio.run(main())
