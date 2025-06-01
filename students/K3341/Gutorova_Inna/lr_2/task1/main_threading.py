import threading
import time


def calculate_sum(start, end, result, index):
    total = 0
    for i in range(start, end + 1):
        total += i
    result[index] = total


def threading_sum():
    num_threads = 4
    total_numbers = 10 ** 6  # Уменьшено для демонстрации
    chunk_size = total_numbers // num_threads
    threads = []
    result = [0] * num_threads

    start_time = time.time()

    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_threads - 1 else total_numbers
        thread = threading.Thread(target=calculate_sum, args=(start, end, result, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(result)
    end_time = time.time()

    print(f"Threading sum: {total_sum}, Time: {end_time - start_time:.4f} seconds")


threading_sum()