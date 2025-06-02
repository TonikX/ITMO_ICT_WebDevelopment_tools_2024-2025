import multiprocessing
import time

def calculate_sum(start, end):
    """Вычисляет сумму чисел в диапазоне [start, end]"""
    return sum(range(start, end + 1))

def process_worker(start, end):
    return calculate_sum(start, end)

def multiprocess_sum(ranges):
    """Вычисляет сумму с использованием процессов"""
    with multiprocessing.Pool(processes=len(ranges)) as pool:
        results = pool.starmap(process_worker, ranges)
    return sum(results)

def main():
    # Разбиваем задачу на части
    num_processes = multiprocessing.cpu_count()
    total_range = 10**9
    chunk_size = total_range // num_processes
    
    ranges = []
    for i in range(num_processes):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_processes - 1 else total_range
        ranges.append((start, end))
    
    # Обычный подход
    start_time = time.time()
    result = multiprocess_sum(ranges)
    end_time = time.time()
    
    print(f"Результат: {result}")
    print(f"Время выполнения (multiprocessing): {end_time - start_time:.2f} секунд")
    
if __name__ == "__main__":
    main()