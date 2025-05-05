import time
import threading


def calculate_sum(start, end, results):
    results.append(sum(range(start, end)))


def main():
    num_threads = 4
    chunk_size = 10_000_000 // num_threads
    threads = []
    results = []
    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size + 1
        thread = threading.Thread(target=calculate_sum, args=(start, end, results))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    total_sum = sum(results)
    print("Threading sum:", total_sum)


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Time (sec): {end_time - start_time:.6f}")