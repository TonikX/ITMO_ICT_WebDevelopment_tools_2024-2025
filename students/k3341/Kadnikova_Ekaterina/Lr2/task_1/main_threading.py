import threading
import time

def calculate_partial_sum(start, end, result, index):
    result[index] = sum(range(start, end))

def main():
    start_time = time.time()
    num_threads = 4
    total = 10_000_000
    chunk_size = total // num_threads
    threads = []
    results = [0] * num_threads

    for i in range(num_threads):
        start = i * chunk_size
        end = total if i == num_threads - 1 else (i + 1) * chunk_size
        thread = threading.Thread(target=calculate_partial_sum, args=(start, end, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(results)
    print(f"Threading result: {total_sum}, Time: {time.time() - start_time:.2f} sec")

if __name__ == "__main__":
    main()