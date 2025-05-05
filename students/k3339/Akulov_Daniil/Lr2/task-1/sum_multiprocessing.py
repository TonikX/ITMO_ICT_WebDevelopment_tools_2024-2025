import time
import multiprocessing


def calculate_sum(start, end, results):
    results.put(sum(range(start, end)))


def main():
    num_threads = 4
    chunk_size = 10_000_000 // num_threads
    threads = []
    results = multiprocessing.Queue()
    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size + 1
        thread = multiprocessing.Process(target=calculate_sum, args=(start, end, results))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    total_sum = 0
    while not results.empty():
        total_sum += results.get()
    print("Multiprocessing sum:", total_sum)


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Time (sec): {end_time - start_time:.6f}")