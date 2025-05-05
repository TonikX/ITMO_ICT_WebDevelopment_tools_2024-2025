import asyncio
import time

async def calculate_sum_of_range(start, end):
    total = 0
    for number in range(start, end):
        total += number
        if number % 10000000 == 0:
            await asyncio.sleep(0)
    return total

async def calculate_sum(limit, num_tasks):
    print(f"Вычисляем сумму от 1 до {limit} с помощью {num_tasks} async-задач...")

    start_time = time.time()

    chunk_size = limit // num_tasks
    ranges = [
        (i * chunk_size + 1, (i + 1) * chunk_size + 1 if i != num_tasks - 1 else limit + 1)
        for i in range(num_tasks)
    ]

    tasks = [
        asyncio.create_task(calculate_sum_of_range(start, end))
        for start, end in ranges
    ]

    results = await asyncio.gather(*tasks)

    total_sum = sum(results)
    end_time = time.time()

    execution_time = end_time - start_time

    print(f"Сумма: {total_sum}")
    print(f"Async-задачи: {num_tasks}")
    print(f"Время выполнения: {execution_time:.3f} секунд")

    return num_tasks, execution_time

if __name__ == "__main__":
    limit = 1000000000
    results = []

    for tasks in range(4, 5):
        num_tasks, execution_time = asyncio.run(calculate_sum(limit, tasks))
        results.append((num_tasks, execution_time))

    print("Результаты:")
    for num_tasks, execution_time in results:
        print(f"{num_tasks} задач — {execution_time:.3f} секунд")
