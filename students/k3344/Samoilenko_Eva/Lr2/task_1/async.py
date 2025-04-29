import asyncio
import time


async def calculate_sum(start, end):
    return sum(range(start, end + 1))


async def async_sum(N, num_tasks=4):
    chunk_size = N // num_tasks  # Разбиваем N на части
    tasks = []

    start_time = time.time()

    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_tasks - 1 else N
        # Создаем задачу для каждой части
        tasks.append(asyncio.create_task(calculate_sum(start, end)))

    # Запускаем все задачи "параллельно" (кооперативная многозадачность)
    results = await asyncio.gather(*tasks)
    total = sum(results)

    end_time = time.time()
    print(f"Async sum: {total}, Time: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    # N = 100_000_000
    N = 1_000_000_000
    asyncio.run(async_sum(N))

# 1 Async sum: 5000000050000000, Time: 2.6105 seconds
# 2 Async sum: 500000000500000000, Time: 27.0212 seconds
