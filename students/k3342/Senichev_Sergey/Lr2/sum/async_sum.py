import asyncio
import time
from typing import List

async def calculate_chunk_sum(start: int, end: int) -> int:
    return sum(range(start, end + 1))

async def calculate_sum(total_numbers: int = 10000000000000, num_workers: int = 4) -> int:
    chunk_size = total_numbers // num_workers
    
    tasks = []
    for i in range(num_workers):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_workers - 1 else total_numbers
        
        task = asyncio.create_task(calculate_chunk_sum(start, end))
        tasks.append(task)
    
    # Ожидание завершения всех задач и суммирование результатов
    results = await asyncio.gather(*tasks)
    return sum(results)

async def main():
    start_time = time.time()
    result = await calculate_sum()
    end_time = time.time()
    
    print(f"async результат: {result}")
    print(f"затраченное время: {end_time - start_time:.2f} секунд")

if __name__ == "__main__":
    asyncio.run(main()) 