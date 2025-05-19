import threading
import time

def calculate_sum(start, end, result, index):
    result[index] = sum(range(start, end))

if __name__ == "__main__":
    start_time = time.time()
    total = 1_000_000_000
    num_threads = 4
    step = total // num_threads
    threads = []
    results = [0] * num_threads

    for i in range(num_threads):
        thread = threading.Thread(target=calculate_sum, args=(i * step, (i + 1) * step, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print(f"Total sum: {sum(results)}")
    print(f"Execution time (threading): {time.time() - start_time:.2f} seconds")
