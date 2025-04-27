import threading
import time


def calculate_sum(start, end, results, index):
    total = sum(range(start, end + 1))
    results[index] = total


def main(N = 10 ** 9, num_parts = 4):
    start_time = time.time()
    threads = []
    results = [0] * num_parts

    chunk_size = N // num_parts
    ranges = []
    for i in range(num_parts):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_parts - 1 else N
        ranges.append((start, end))

    for i, (start, end) in enumerate(ranges):
        thread = threading.Thread(target = calculate_sum, args = (start, end, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(results)
    end_time = time.time()

    print(f"Sum: {total_sum}")
    print(f"Time: {end_time - start_time:.2f} seconds")
