import threading
import time

def calculate_sum(start, end):
    """Вычисляет сумму чисел в диапазоне [start, end]"""
    return sum(range(start, end + 1))

def threaded_sum(ranges):
    """Вычисляет сумму с использованием потоков"""
    results = [0] * len(ranges)
    
    def worker(index, start, end):
        results[index] = calculate_sum(start, end)
    
    threads = []
    for i, (start, end) in enumerate(ranges):
        thread = threading.Thread(target=worker, args=(i, start, end))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return sum(results)

def main():
    # Разбиваем задачу на части
    num_threads = 1
    total_range = 10**9
    chunk_size = total_range // num_threads
    
    ranges = []
    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_threads - 1 else total_range
        ranges.append((start, end))
    
    start_time = time.time()
    result = threaded_sum(ranges)
    end_time = time.time()
    
    print(f"Результат: {result}")
    print(f"Время выполнения (threading): {end_time - start_time:.2f} секунд")

if __name__ == "__main__":
    main()