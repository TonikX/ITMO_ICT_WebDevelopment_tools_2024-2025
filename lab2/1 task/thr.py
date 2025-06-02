import threading
import time


def calculate_sum(start, end, results, index):
    total = 0
    for i in range(start, end + 1):
        total += i
    results[index] = total


def main():
    start_time = time.time()

    n = 10 ** 9
    num_threads = 8
    chunk_size = n // num_threads

    results = [0] * num_threads
    threads = []

    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_threads - 1 else n

        thread = threading.Thread(target=calculate_sum, args=(start, end, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(results)
    end_time = time.time()

    print(f"Итоговая сумма: {total_sum}")
    print(f"Время выполнения: {end_time - start_time:.2f} секунд")
    print(f"Количество потоков: {num_threads}")


if __name__ == "__main__":
    main()