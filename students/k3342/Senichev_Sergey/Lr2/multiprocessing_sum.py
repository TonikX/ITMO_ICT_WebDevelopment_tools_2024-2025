import multiprocessing
import time
from typing import List

def calculate_chunk_sum(start: int, end: int, result: List[int], index: int) -> None:
    """Вычисляет сумму для части чисел и сохраняет её в списке результатов."""
    chunk_sum = sum(range(start, end + 1))
    result[index] = chunk_sum

def calculate_sum() -> int:
    """Вычисляет сумму чисел от 1 до 10000000000000 с использованием мультипроцессинга."""
    total_numbers = 10000000000000
    num_processes = multiprocessing.cpu_count()  # Используем количество ядер CPU
    chunk_size = total_numbers // num_processes
    
    # Создаем общий массив для хранения результатов
    manager = multiprocessing.Manager()
    results = manager.list([0] * num_processes)
    processes = []
    
    # Создание и запуск процессов
    for i in range(num_processes):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_processes - 1 else total_numbers
        
        process = multiprocessing.Process(
            target=calculate_chunk_sum,
            args=(start, end, results, i)
        )
        processes.append(process)
        process.start()
    
    # Ожидание завершения всех процессов
    for process in processes:
        process.join()
    
    # Суммирование всех результатов
    return sum(results)

if __name__ == "__main__":
    start_time = time.time()
    result = calculate_sum()
    end_time = time.time()
    
    print(f"multiprocessing результат: {result}")
    print(f"затраченное время: {end_time - start_time:.2f} секунд") 