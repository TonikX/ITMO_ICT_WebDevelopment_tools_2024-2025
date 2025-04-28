import multiprocessing
import time
from typing import List

def calculate_chunk_sum(start: int, end: int, result: List[int], index: int) -> None:
    chunk_sum = sum(range(start, end + 1))
    result[index] = chunk_sum

def calculate_sum(total_numbers: int = 10000000000000, num_workers: int = None) -> int:
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()
    
    chunk_size = total_numbers // num_workers
    
    manager = multiprocessing.Manager()
    results = manager.list([0] * num_workers)
    processes = []
    
    for i in range(num_workers):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_workers - 1 else total_numbers
        
        process = multiprocessing.Process(
            target=calculate_chunk_sum,
            args=(start, end, results, i)
        )
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()
    
    return sum(results)

if __name__ == "__main__":
    start_time = time.time()
    result = calculate_sum()
    end_time = time.time()
    
    print(f"multiprocessing результат: {result}")
    print(f"затраченное время: {end_time - start_time:.2f} секунд") 