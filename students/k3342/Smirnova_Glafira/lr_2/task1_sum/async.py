import asyncio
import time


async def calculate_partial_sum(start, end):
    return sum(range(start, end + 1))


async def main():
    n = 1_000_000_000
    num_tasks = 1000
    chunk_size = n // num_tasks

    print(f"Вычисление суммы чисел от 1 до {n:,}")
    print(f"Используется {num_tasks} асинхронных задач...")

    # корутины
    tasks = []
    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_tasks - 1 else n
        tasks.append(calculate_partial_sum(start, end))

    start_time = time.time()

    # запуск всех задач параллельно
    partial_sums = await asyncio.gather(*tasks)
    total_sum = sum(partial_sums)

    end_time = time.time()

    expected_sum = n * (n + 1) // 2
    is_correct = total_sum == expected_sum

    print("\nРезультат:")
    print(f"Вычисленная сумма: {total_sum}")
    print(f"Ожидаемая сумма:   {expected_sum}")
    print(f"Совпадает: {'Да' if is_correct else 'Нет'}")
    print(f"Время выполнения: {end_time - start_time:.6f} секунд")


if __name__ == "__main__":
    asyncio.run(main())

# Время выполнения: 34.351786 секунд