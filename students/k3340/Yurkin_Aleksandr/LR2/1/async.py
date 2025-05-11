import asyncio
import time

def calculate_sum(start, end):
    return sum(range(start, end + 1))

async def main():
    N = 5000000000
    num_tasks = 4
    chunk_size = N // num_tasks
    ranges = []
    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_tasks - 1 else N
        ranges.append((start, end))

    loop = asyncio.get_running_loop()
    start_time = time.time()

    tasks = [loop.run_in_executor(None, calculate_sum, s, e) for s, e in ranges]
    results = await asyncio.gather(*tasks)

    total = sum(results)
    end_time = time.time()

    print(f"Async Total: {total}")
    print(f"Async Time: {end_time - start_time:.2f} seconds")

if __name__ == '__main__':
    asyncio.run(main())
