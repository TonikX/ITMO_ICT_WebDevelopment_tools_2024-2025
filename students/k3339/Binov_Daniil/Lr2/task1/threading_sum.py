import time
import threading

def calculate_partial_sum(start, end):
    return end * (end + 1) // 2 - (start - 1) * start // 2

N = 10000000000000
NUM_THREADS = 4
chunk_size = N // NUM_THREADS

start_time = time.time()

threads = []
results = [0] * NUM_THREADS

for i in range(NUM_THREADS):
    start = i * chunk_size + 1
    end = (i + 1) * chunk_size if i < NUM_THREADS - 1 else N
    def target(idx, s, e):
        results[idx] = calculate_partial_sum(s, e)
    thread = threading.Thread(target=target, args=(i, start, end))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

total_sum = sum(results)

end_time = time.time()
print(f"Threading sum: {total_sum}")
print(f"Threading time: {end_time - start_time} seconds")