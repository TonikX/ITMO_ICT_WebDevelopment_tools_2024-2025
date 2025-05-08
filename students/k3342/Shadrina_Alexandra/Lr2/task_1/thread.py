import threading
import time


def calculate_partial_sum(start, end, result, index):
    result[index] = sum(range(start, end))


def threaded_sum():
    num_threads = 4
    total = 1000000000
    step = total // num_threads
    threads = []
    results = [0] * num_threads

    for i in range(num_threads):
        start = i * step
        end = (i + 1) * step if i != num_threads - 1 else total
        thread = threading.Thread(target=calculate_partial_sum, args=(start, end, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return sum(results)


start_time = time.time()
result = threaded_sum()
print("Threading result:", result)
print("Execution time:", time.time() - start_time, "seconds")
