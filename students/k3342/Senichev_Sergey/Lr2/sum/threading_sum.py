import threading
import time
from typing import List

def calculate_chunk_sum(start: int, end: int, result: List[int], index: int) -> None:
    chunk_sum = sum(range(start, end + 1))
    result[index] = chunk_sum

def calculate_sum(total_numbers: int = 10000000000000, num_workers: int = 4) -> int:
    chunk_size = total_numbers // num_workers
    
    results = [0] * num_workers
    threads = []
    
    for i in range(num_workers):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_workers - 1 else total_numbers
        
        thread = threading.Thread(
            target=calculate_chunk_sum,
            args=(start, end, results, i)
        )
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return sum(results)

if __name__ == "__main__":
    start_time = time.time()
    result = calculate_sum()
    end_time = time.time()
    
    print(f"threading результат: {result}")
    print(f"затраченное время: {end_time - start_time:.2f} секунд") 