import threading
import time

partial_sums = []
lock = threading.Lock()


def calculate_sum(start, end):
    local_sum = 0
    for i in range(start, end + 1):
        local_sum += i
    with lock:
        partial_sums.append(local_sum)


if __name__ == "__main__":
    TOTAL_SUM_UP_TO = 100_000_000
    NUM_THREADS = 4
    total_sum = 0
    threads = []

    chunk_size = TOTAL_SUM_UP_TO // NUM_THREADS
    start_time = time.perf_counter()

    for i in range(NUM_THREADS):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < NUM_THREADS - 1 else TOTAL_SUM_UP_TO
        thread = threading.Thread(target=calculate_sum, args=(start, end))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(partial_sums)

    end_time = time.perf_counter()

    print(f"Threading")
    print(f"Calculated sum: {total_sum}")
    print(f"Execution time: {end_time - start_time:.2f} seconds")