import threading
import time

def partial_sum(start, end, result, index):
    result[index] = sum(range(start, end))

def calculate_sum():
    num_threads = 4
    n = 1_000_000_000
    step = n // num_threads
    threads = []
    result = [0] * num_threads

    for i in range(num_threads):
        start = i * step
        end = n if i == num_threads - 1 else (i + 1) * step
        t = threading.Thread(target=partial_sum, args=(start, end, result, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return sum(result)
