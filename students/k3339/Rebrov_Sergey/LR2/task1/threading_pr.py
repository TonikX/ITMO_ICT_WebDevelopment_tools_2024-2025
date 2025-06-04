import time
import threading


def partial_sum(start, end, result, index):
    result[index] = sum(range(start, end))


def calculate_sum(total=10 ** 9, num_threads=32):
    step = total // num_threads
    threads = []
    results = [0] * num_threads

    for i in range(num_threads):
        start = i * step
        end = total if i == num_threads - 1 else (i + 1) * step
        thread = threading.Thread(target=partial_sum, args=(start, end, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return sum(results)


if __name__ == "__main__":
    start_time = time.time()
    print(f"Сумма: {calculate_sum()}")
    print(f"Время: {time.time() - start_time:.2f} сек")
