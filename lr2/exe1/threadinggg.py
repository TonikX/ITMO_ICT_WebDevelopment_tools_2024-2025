import threading
import time

TOTAL = 1_000_000_000
NUM_THREADS = 4

def partial_sum(start, end, result, index, results):
    results[index] = sum(range(start, end + 1))

def calculate_sum():
    chunk_size = TOTAL // NUM_THREADS
    threads = []
    results = [0] * NUM_THREADS

    for i in range(NUM_THREADS):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != NUM_THREADS - 1 else TOTAL
        thread = threading.Thread(target=partial_sum, args=(start, end, results, i, results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return sum(results)

if __name__ == "__main__":
    start_time = time.time()
    total_sum = calculate_sum()
    print(f"Threading: Сумма равна {total_sum}")
    print(f"Время выполнения: {time.time() - start_time:.4f} секунд")