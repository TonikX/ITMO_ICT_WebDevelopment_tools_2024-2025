import threading
import time


def calculate_sum(start: int, end: int) -> int:
    return (end - start + 1) * (start + end) // 2

def worker(start: int, end: int, result_list: list, index: int):
    result_list[index] = calculate_sum(start, end)

if __name__ == "__main__":
    N = 10_000_000_000_000
    num_threads = 4
    chunk = N // num_threads

    results = [0] * num_threads
    threads = []

    t0 = time.perf_counter()
    for i in range(num_threads):
        s = i * chunk + 1
        e = (i + 1) * chunk if i < num_threads - 1 else N
        th = threading.Thread(target=worker, args=(s, e, results, i))
        th.start()
        threads.append(th)

    for th in threads:
        th.join()
    total_sum = sum(results)
    t1 = time.perf_counter()

    print(f"Threading: sum = {total_sum}, time = {t1 - t0:.6f} s")