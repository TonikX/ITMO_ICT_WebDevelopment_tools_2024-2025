import threading
import time

N = 10**9
PARTS = 5


def calculate_range(start: int, end: int) -> int:
    return sum(range(start, end))


def calculate_sum_threading() -> int:
    chunk_size = N // PARTS
    threads = []
    results = [0] * PARTS

    def worker(idx, start, end):
        results[idx] = calculate_range(start, end)

    for i in range(PARTS):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size + 1
        t = threading.Thread(target=worker, args=(i, start, end))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return sum(results)


if __name__ == "__main__":
    t0 = time.time()
    result_thread = calculate_sum_threading()
    t1 = time.time()
    print(f"Threading result: {result_thread}, time: {t1 - t0:.2f}s")