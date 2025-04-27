import threading
import time

def calculate_sum_of_range(start, end, result_list, index):
    total = 0
    for number in range(start, end):
        total += number
    result_list[index] = total

def calculate_sum(limit, num_threads):
    print(f"Вычисляем сумму от 1 до {limit} с помощью {num_threads} потоков...")

    start_time = time.time()

    results = [0] * num_threads
    threads = []
    chunk_size = limit // num_threads

    ranges = [
        (i * chunk_size + 1, (i + 1) * chunk_size + 1 if i != num_threads - 1 else limit + 1)
        for i in range(num_threads)
    ]

    for i, (start, end) in enumerate(ranges):
        thread = threading.Thread(target=calculate_sum_of_range, args=(start, end, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(results)
    end_time = time.time()

    print(f"Сумма: {total_sum}")
    print(f"Потоки: {num_threads}")
    print(f"Время выполнения: {end_time - start_time:.3f} секунд")

if __name__ == "__main__":
    limit = 1000000000
    for threads in range(4, 5):
        calculate_sum(limit, threads)
