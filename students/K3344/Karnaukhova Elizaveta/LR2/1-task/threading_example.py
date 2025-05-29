import threading
import time


def calculate_sum(start, end, result, index):
    total = 0
    for i in range(start, end + 1):
        total += i
    result[index] = total


def threading_sum(N, num_threads=4):
    chunk_size = N // num_threads
    threads = []
    result = [0] * num_threads

    start_time = time.time()

    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_threads - 1 else N
        thread = threading.Thread(target=calculate_sum, args=(start, end, result, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total = sum(result)

    end_time = time.time()
    print(f"Threading sum: {total}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    N = 1_000_000_000
    threading_sum(N)

# first tray Threading sum: 500000000500000000
# Time taken: 28.3993 seconds

# second tray Threading sum: 500000000500000000
# Time taken: 29.0507 seconds
