import threading
import time

N = 1_000_000_000
THREADS = 4
results = []

def calculate_sum(start, end):
    results.append(sum(range(start, end)))

def main():
    start_time = time.time()
    step = N // THREADS
    threads = []

    for i in range(THREADS):
        start_i = i * step
        end_i = N if i == THREADS - 1 else (i + 1) * step
        t = threading.Thread(target=calculate_sum, args=(start_i, end_i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total = sum(results)
    print("Threading Result:", total)
    print("Time:", time.time() - start_time)

if __name__ == "__main__":
    main()
