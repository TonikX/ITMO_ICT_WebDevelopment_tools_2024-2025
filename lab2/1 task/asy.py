import asyncio
import time


async def calculate_sum(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


async def main():
    start_time = time.time()

    n = 10 ** 9
    num_tasks = 8
    chunk_size = n // num_tasks

    tasks = []
    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_tasks - 1 else n
        tasks.append(calculate_sum(start, end))

    results = await asyncio.gather(*tasks)

    total_sum = sum(results)
    end_time = time.time()

    print(f"Итоговая сумма: {total_sum}")
    print(f"Время выполнения: {end_time - start_time:.2f} секунд")
    print(f"Количество задач: {num_tasks}")


if __name__ == "__main__":
    asyncio.run(main())