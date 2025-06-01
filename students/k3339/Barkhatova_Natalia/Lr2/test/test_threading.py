import threading
import time

N = 10_000_000
NUM_THREADS = 4
results = [0] * NUM_THREADS


def calculate_sum(start, end, index):
    results[index] = sum(range(start, end))


def main():
    threads = []
    chunk_size = N // NUM_THREADS

    for i in range(NUM_THREADS):
        start = i * chunk_size
        end = N if i == NUM_THREADS - 1 else (i + 1) * chunk_size
        thread = threading.Thread(target=calculate_sum, args=(start, end, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total = sum(results)
    print(f"Сумма: {total}")


if __name__ == "__main__":
    start_time = time.time()
    main()
    duration = time.time() - start_time
    print(f"Затрачено времени: {duration:.2f} секунд")
