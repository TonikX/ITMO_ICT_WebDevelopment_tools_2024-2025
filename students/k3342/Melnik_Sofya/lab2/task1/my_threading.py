import threading
import time

total_sum = 0
lock = threading.Lock()

def calculate_partial_sum(start, end):
    global total_sum
    partial_sum = sum(range(start, end))
    with lock:
        total_sum += partial_sum

def calculate_sum(n, num_threads=4):
    global total_sum
    total_sum = 0
    threads = []
    step = n // num_threads

    for i in range(num_threads):
        start = i * step + 1
        end = (i + 1) * step + 1 if i != num_threads - 1 else n + 1
        thread = threading.Thread(target=calculate_partial_sum, args=(start, end))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return total_sum

if __name__ == "__main__":
    n = 1_000_000_000
    start_time = time.time()
    result = calculate_sum(n)
    end_time = time.time()
    print(f"Threading result: {result}")
    print(f"Execution time: {end_time - start_time:.2f} seconds")
