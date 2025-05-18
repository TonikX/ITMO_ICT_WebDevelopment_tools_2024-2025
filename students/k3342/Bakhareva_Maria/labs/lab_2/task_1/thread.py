import threading
import time

def calculate_sum(start: int, end: int) -> int:
    return (end - start + 1) * (start + end) // 2

def thread_task(start: int, end: int, storage: list, idx: int):
    storage[idx] = calculate_sum(start, end)

if __name__ == "__main__":
    upper_limit = 10_000_000_000_000
    thread_count = 4
    segment = upper_limit // thread_count

    results = [0] * thread_count
    thread_pool = []

    start_time = time.perf_counter()
    for i in range(thread_count):
        begin = i * segment + 1
        finish = (i + 1) * segment if i < thread_count - 1 else upper_limit
        t = threading.Thread(target=thread_task, args=(begin, finish, results, i))
        t.start()
        thread_pool.append(t)

    for t in thread_pool:
        t.join()

    total = sum(results)
    end_time = time.perf_counter()

    print(f"Threading: result = {total}, duration = {end_time - start_time:.6f} seconds")
