import asyncio
import multiprocessing
import time

async def calculate(start, end):
    local_sum = 0
    for i in range(start, end):
        local_sum += i
    return local_sum

async def main():

    n = 1000000000
    n_process = multiprocessing.cpu_count()
    n_calculate_one = n // n_process

    start_time = time.perf_counter()
    tasks = []
    for start_calculate in range(0, n, n_calculate_one):
        task = asyncio.create_task(calculate(start_calculate, start_calculate + n_calculate_one))
        tasks.append(task)
    

    results = await asyncio.gather(*tasks)

    print(sum(results))

    print(f"Время: {time.perf_counter() - start_time}")

if __name__ == "__main__":
    asyncio.run(main())