import threading
import time

def partial_sum(start, end, res, lock):
    total = sum(range(start, end))
    with lock:
        res.append(total)

def main():
    n = 1_000_000_000
    num_threads = 4
    chunk_size = n // num_threads

    results = []
    lock = threading.Lock()
    threads = []

    start_time = time.time()


    for i in range(0, n, chunk_size):
        start = i + 1
        end = min(i + chunk_size, n) + 1

        t = threading.Thread(
            target=partial_sum,
            args=(start, end, results, lock))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total = sum(results)
    end_time = time.time()

    print(f"Сумма: {total}, время: {end_time - start_time:.2f} сек")

if __name__ == '__main__':
    main()