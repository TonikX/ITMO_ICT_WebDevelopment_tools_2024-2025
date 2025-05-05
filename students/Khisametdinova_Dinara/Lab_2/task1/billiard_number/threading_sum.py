import threading
import time

def partial_sum(start, end, result, index):
    result[index] = sum(range(start, end + 1))

def calculate_sum():
    total_start = 1
    total_end = 1_000_000_000
    num_threads = 8
    step = (total_end - total_start + 1) // num_threads

    results = [0] * num_threads
    threads = []

    for i in range(num_threads):
        segment_start = total_start + i * step
        segment_end = segment_start + step - 1 if i < num_threads - 1 else total_end
        thread = threading.Thread(target=partial_sum, args=(segment_start, segment_end, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return sum(results)

def main():
    start = time.time()
    total = calculate_sum()
    end = time.time()
    print(f"sum: {total}")
    print(f"time: {end - start:.2f} seconds")

if __name__ == "__main__":
    main()
