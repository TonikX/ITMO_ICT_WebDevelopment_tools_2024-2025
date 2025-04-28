import time
import psutil
import os
import logging
import asyncio
from typing import Callable, Any

# Создаем папку data, если она не существует
os.makedirs('data', exist_ok=True)

# Настраиваем логирование
logging.basicConfig(
    filename='data/sum_tests.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

async def log_sum_operation_async(method: str, func: Callable, target_power: int, num_workers: int = None) -> None:
    """Логирует результаты работы асинхронной функции суммирования."""
    process = psutil.Process()
    start_memory = process.memory_info().rss / 1024 / 1024  # в МБ
    
    # Преобразуем target_power в total_numbers (10^target_power)
    total_numbers = 10 ** target_power
    
    start_time = time.time()
    result = await func(total_numbers, num_workers)
    end_time = time.time()
    
    end_memory = process.memory_info().rss / 1024 / 1024  # в МБ
    memory_used = end_memory - start_memory
    
    # Логирование в файл
    logging.info(f"{method.upper()} TEST")
    logging.info(f"Target power: {target_power} (10^{target_power} = {total_numbers})")
    if num_workers:
        logging.info(f"Workers: {num_workers}")
    logging.info(f"Time: {end_time - start_time:.2f} seconds")
    logging.info(f"Memory used: {memory_used:.2f} MB")
    logging.info(f"Result: {result}")
    logging.info("-" * 50)
    
    # Вывод в консоль
    print(f"{method.upper()} TEST")
    print(f"Target power: {target_power} (10^{target_power} = {total_numbers})")
    if num_workers:
        print(f"Workers: {num_workers}")
    print(f"Time: {end_time - start_time:.2f} seconds")
    print(f"Memory used: {memory_used:.2f} MB")
    print(f"Result: {result}")
    print("-" * 50)

def log_sum_operation(method: str, func: Callable, target_power: int, num_workers: int = None) -> None:
    """Логирует результаты работы функции суммирования."""
    process = psutil.Process()
    start_memory = process.memory_info().rss / 1024 / 1024  # в МБ
    
    # Преобразуем target_power в total_numbers (10^target_power)
    total_numbers = 10 ** target_power
    
    start_time = time.time()
    result = func(total_numbers, num_workers)
    end_time = time.time()
    
    end_memory = process.memory_info().rss / 1024 / 1024  # в МБ
    memory_used = end_memory - start_memory
    
    # Логирование в файл
    logging.info(f"{method.upper()} TEST")
    logging.info(f"Target power: {target_power} (10^{target_power} = {total_numbers})")
    if num_workers:
        logging.info(f"Workers: {num_workers}")
    logging.info(f"Time: {end_time - start_time:.2f} seconds")
    logging.info(f"Memory used: {memory_used:.2f} MB")
    logging.info(f"Result: {result}")
    logging.info("-" * 50)
    
    # Вывод в консоль
    print(f"{method.upper()} TEST")
    print(f"Target power: {target_power} (10^{target_power} = {total_numbers})")
    if num_workers:
        print(f"Workers: {num_workers}")
    print(f"Time: {end_time - start_time:.2f} seconds")
    print(f"Memory used: {memory_used:.2f} MB")
    print(f"Result: {result}")
    print("-" * 50) 