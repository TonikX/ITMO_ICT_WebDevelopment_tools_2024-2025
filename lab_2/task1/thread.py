import threading
import time

N = 1_000_000_000
THREADS = 4
results = [0] * THREADS


def calculate_sum(start, end, index):
    results[index] = sum(range(start, end))


def run_threading():
    threads = []
    step = N // THREADS
    start_time = time.time()

    for i in range(THREADS):
        start = i * step
        end = N if i == THREADS - 1 else (i + 1) * step
        t = threading.Thread(target=calculate_sum, args=(start, end, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total = sum(results)
    print("Threading Total:", total)
    print("Threading Time:", time.time() - start_time)

if __name__ == "__main__":
    run_threading()
