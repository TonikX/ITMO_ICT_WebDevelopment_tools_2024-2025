import time
import psutil
import os
import logging
from typing import List, Callable, Any

# Создаем папку data, если она не существует
os.makedirs('data', exist_ok=True)

# Настраиваем логирование
logging.basicConfig(
    filename='data/parser_tests.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def log_parser_operation(method: str, func: Callable, urls: List[str], num_workers: int = None) -> None:
    """Логирует результаты работы парсера."""
    process = psutil.Process()
    start_memory = process.memory_info().rss / 1024 / 1024  # в МБ
    
    start_time = time.time()
    results = func(urls, num_workers)
    end_time = time.time()
    
    end_memory = process.memory_info().rss / 1024 / 1024  # в МБ
    memory_used = end_memory - start_memory
    
    logging.info(f"{method.upper()} TEST")
    logging.info(f"URLs processed: {len(urls)}")
    if num_workers:
        logging.info(f"Workers: {num_workers}")
    logging.info(f"Time: {end_time - start_time:.2f} seconds")
    logging.info(f"Memory used: {memory_used:.2f} MB")
    logging.info(f"Results: {len(results)} items")
    logging.info("-" * 50)

async def log_parser_operation_async(method: str, func: Callable, urls: List[str], num_workers: int = None) -> None:
    """Логирует результаты работы асинхронного парсера."""
    process = psutil.Process()
    start_memory = process.memory_info().rss / 1024 / 1024  # в МБ
    
    start_time = time.time()
    results = await func(urls)
    end_time = time.time()
    
    end_memory = process.memory_info().rss / 1024 / 1024  # в МБ
    memory_used = end_memory - start_memory
    
    # Логирование в файл
    logging.info(f"{method.upper()} TEST")
    logging.info(f"URLs processed: {len(urls)}")
    if num_workers:
        logging.info(f"Workers: {num_workers}")
    logging.info(f"Time: {end_time - start_time:.2f} seconds")
    logging.info(f"Memory used: {memory_used:.2f} MB")
    logging.info(f"Results: {len(results)} items")
    logging.info("-" * 50)
    
    # Вывод в консоль
    print(f"{method.upper()} TEST")
    print(f"URLs processed: {len(urls)}")
    if num_workers:
        print(f"Workers: {num_workers}")
    print(f"Time: {end_time - start_time:.2f} seconds")
    print(f"Memory used: {memory_used:.2f} MB")
    print(f"Results: {len(results)} items")
    print("-" * 50)
    
    # Вывод результатов парсинга
    for result in results:
        print(f"Успешно распарсено и сохранено: {result['url']} (время: {result['parsing_time']:.2f} сек)") 