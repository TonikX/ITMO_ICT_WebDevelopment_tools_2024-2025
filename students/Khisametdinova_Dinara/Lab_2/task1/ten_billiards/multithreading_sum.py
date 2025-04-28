import threading
import time

def partial_sum(start, end, result, index):
    n = end - start + 1
    result[index] = (start + end) * n // 2

def calculate_sum():
    total_start = 1
    total_end = 10_000_000_000_000
    num_threads = 8
    step = (total_end - total_start + 1) // num_threads

    threads = []
    results = [0] * num_threads

    for i in range(num_threads):
        start = total_start + i * step
        end = start + step - 1 if i != num_threads - 1 else total_end
        t = threading.Thread(target=partial_sum, args=(start, end, results, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return sum(results)

if __name__ == "__main__":
    start_time = time.time()
    total = calculate_sum()
    end_time = time.time()
    print(f"sum: {total}")
    print(f"time: {end_time - start_time:.2f} seconds")
