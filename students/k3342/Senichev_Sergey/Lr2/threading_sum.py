import threading
import time
from typing import List

def calculate_chunk_sum(start: int, end: int, result: List[int], index: int) -> None:
    """Вычисляет сумму для части чисел и сохраняет её в списке результатов."""
    chunk_sum = sum(range(start, end + 1))
    result[index] = chunk_sum

def calculate_sum() -> int:
    """Вычисляет сумму чисел от 1 до 10000000000000 с использованием потоков."""
    total_numbers = 10000000000000
    num_threads = 4  # Количество потоков
    chunk_size = total_numbers // num_threads
    
    # Список для хранения результатов от каждого потока
    results = [0] * num_threads
    threads = []
    
    # Создание и запуск потоков
    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_threads - 1 else total_numbers
        
        thread = threading.Thread(
            target=calculate_chunk_sum,
            args=(start, end, results, i)
        )
        threads.append(thread)
        thread.start()
    
    # Ожидание завершения всех потоков
    for thread in threads:
        thread.join()
    
    # Суммирование всех результатов
    return sum(results)

if __name__ == "__main__":
    start_time = time.time()
    result = calculate_sum()
    end_time = time.time()
    
    print(f"threading результат: {result}")
    print(f"затраченное время: {end_time - start_time:.2f} секунд") 