import threading
import time

def calculate_partial_sum(start, end, result, index):
    partial_sum = sum(range(start, end + 1))
    result[index] = partial_sum

def main():
    n = 1000000000
    num_threads = 4
    chunk_size = n // num_threads
    result = [0] * num_threads
    threads = []

    start_time = time.time()

    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_threads - 1 else n
        thread = threading.Thread(
            target=calculate_partial_sum,
            args=(start, end, result, i)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(result)
    end_time = time.time()

    expected_sum = n * (n + 1) // 2
    is_correct = (total_sum == expected_sum)

    print("\nРезультат:")
    print(f"Вычисленная сумма: {total_sum}")
    print(f"Ожидаемая сумма:   {expected_sum}")
    print(f"Совпадает: {'Да' if is_correct else 'Нет'}")
    print(f"Время выполнения: {end_time - start_time:.6f} секунд")

if __name__ == "__main__":
    main()

# Время выполнения: 35.219985 секунд
