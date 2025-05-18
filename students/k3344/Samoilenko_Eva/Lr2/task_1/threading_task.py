import threading
import time


def calculate_sum(start, end, result, index):
    result[index] = sum(range(start, end + 1))


def threading_sum(N, num_threads=4):
    chunk_size = N // num_threads  # Разбиваем N на части
    threads = []
    results = [0] * num_threads

    start_time = time.time()

    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_threads - 1 else N
        # Создаем поток для каждой части
        thread = threading.Thread(target=calculate_sum, args=(start, end, results, i))
        threads.append(thread)
        thread.start()  # Запускаем потоки параллельно

    for thread in threads:
        thread.join()

    total = sum(results)

    end_time = time.time()
    print(f"Threading sum: {total}, Time: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    # N = 100_000_000
    N = 1_000_000_000
    threading_sum(N)

# 1 Threading sum: 5000000050000000, Time: 2.5699 seconds
# 2 Threading sum: 500000000500000000, Time: 25.6159 seconds
