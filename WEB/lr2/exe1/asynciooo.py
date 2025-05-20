import asyncio
import time

TOTAL = 1_000_000_000
NUM_TASKS = 4

def sync_partial_sum(start, end):
    return sum(range(start, end + 1))

async def async_partial_sum(start, end):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_partial_sum, start, end)

async def calculate_sum():
    chunk_size = TOTAL // NUM_TASKS
    tasks = []

    for i in range(NUM_TASKS):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != NUM_TASKS - 1 else TOTAL
        tasks.append(async_partial_sum(start, end))

    results = await asyncio.gather(*tasks)
    return sum(results)

if __name__ == "__main__":
    start_time = time.time()
    total_sum = asyncio.run(calculate_sum())
    print(f"Asyncio: Сумма равна {total_sum}")
    print(f"Время выполнения: {time.time() - start_time:.4f} секунд")