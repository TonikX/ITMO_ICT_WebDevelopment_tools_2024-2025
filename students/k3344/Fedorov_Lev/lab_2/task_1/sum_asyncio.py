import asyncio
import time


async def calculate_sum_part_async(start, end, task_id):
    """Асинхронно вычисляет сумму чисел в заданном диапазоне"""
    partial_sum = 0
    for i in range(start, end + 1):
        partial_sum += i
        if i % 1_000_000 == 0:
            await asyncio.sleep(0.000001)
    print(f"таск {task_id}: вычислил с {start} по {end} = {partial_sum}")
    return partial_sum


async def calculate_sum_async(n, num_tasks=4):
    """Вычисляет сумму чисел от 1 до n используя async/await"""
    chunk_size = n // num_tasks

    start_time = time.time()

    # Создаем список задач
    tasks = []
    for i in range(num_tasks):
        start = i * chunk_size + 1
        if i == num_tasks - 1:
            end = n  # Последняя задача обрабатывает оставшиеся числа
        else:
            end = (i + 1) * chunk_size

        task = calculate_sum_part_async(start, end, i)
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    total_sum = sum(results)
    end_time = time.time()

    print(f"\nAsync сумма: {total_sum}")
    print(f"время затрачено: {end_time - start_time:.2f} seconds")
    return total_sum


if __name__ == "__main__":
    n = 10_000_000
    asyncio.run(calculate_sum_async(n))
    # 0.56 sec