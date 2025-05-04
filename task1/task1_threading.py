# threading_sum.py
import threading
import time

TOTAL = 10_000_000_000
NUM_WORKERS = 4
results = [0] * NUM_WORKERS

def calculate_sum(start, end, index):
    results[index] = sum(range(start, end + 1))

def main():
    step = TOTAL // NUM_WORKERS
    threads = []

    start_time = time.time()

    for i in range(NUM_WORKERS):
        start = i * step + 1
        end = (i + 1) * step if i != NUM_WORKERS - 1 else TOTAL
        thread = threading.Thread(target=calculate_sum, args=(start, end, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total = sum(results)
    duration = time.time() - start_time

    print(f"Threading total sum: {total}")
    print(f"Threading duration: {duration:.2f} seconds")

if __name__ == "__main__":
    main()
