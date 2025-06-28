import asyncio
import time

async def calculate_sum(start, end):
    partial_sum = 0
    for i in range(start, end + 1):
        partial_sum += i
    return partial_sum

async def main():
    n = 10**8
    num_tasks = 4
    chunk_size = n // num_tasks
    
    tasks = []
    start_time = time.time()
    
    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_tasks - 1 else n
        tasks.append(calculate_sum(start, end))
    
    results = await asyncio.gather(*tasks)
    total_sum = sum(results)
    end_time = time.time()
    
    print(f"Async result: {total_sum}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())