import threading
import time

def calculate_sum(start: int, end: int) -> int:
    total = 0
    for i in range(start, end + 1):
        total += i
    return total

def worker(start: int, end: int, idx: int, results: dict):
    results[idx] = calculate_sum(start, end)

def main():
    N = 100_000_000
    num_threads = 4
    chunk = N // num_threads

    threads = []
    results = {}

    t0 = time.time()
    for i in range(num_threads):
        s = i * chunk + 1
        e = (i + 1) * chunk if i < num_threads - 1 else N
        th = threading.Thread(target=worker, args=(s, e, i, results))
        th.start()
        threads.append(th)

    for th in threads:
        th.join()
    total = sum(results.values())
    t1 = time.time()

    print(f"Threading: сумма = {total}, время = {t1 - t0:.3f} сек")

if __name__ == "__main__":
    main()
