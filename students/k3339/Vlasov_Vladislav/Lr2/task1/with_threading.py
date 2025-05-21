import threading
import time

def calculate(start, end, results: list):
    local_sum = 0
    for i in range(start, end):
        local_sum += i
    results.append(local_sum)


n = 1000000000
n_thread = 100

n_calculate_one = n // n_thread

start_time = time.perf_counter()

results = []
threads: list[threading.Thread] = []

for start_calculate in range(0, n, n_calculate_one):
    thread = threading.Thread(target=calculate, args=(start_calculate, start_calculate + n_calculate_one, results))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

print(sum(results))

print(f"Время: {time.perf_counter() - start_time}")