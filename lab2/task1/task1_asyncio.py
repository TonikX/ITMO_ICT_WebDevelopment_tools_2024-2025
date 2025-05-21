import asyncio
import time

async def calculate_sum(start, end):
    """Асинхронно вычисляет сумму чисел в диапазоне [start, end]"""
    return sum(range(start, end + 1))

async def async_sum(ranges):
    tasks = [calculate_sum(start, end) for start, end in ranges]
    results = await asyncio.gather(*tasks)
    return sum(results)

async def main():
    # Разбиваем задачу на части
    num_tasks = 8
    total_range = 100_000_000
    chunk_size = total_range // num_tasks
    
    ranges = []
    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_tasks - 1 else total_range
        ranges.append((start, end))
    
    start_time = time.time()
    result = await async_sum(ranges)
    end_time = time.time()
    
    print(f"Результат: {result}")
    print(f"Время выполнения (asyncio): {end_time - start_time:.2f} секунд")

if __name__ == "__main__":
    asyncio.run(main())
