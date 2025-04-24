import threading
import time


def calculate_sum(start, end, results, index):
    results[index] = sum(range(start, end))


def main():
    total = 10_000_000
    num_threads = 4
    step = total // num_threads
    threads = []
    results = [0] * num_threads

    start_time = time.time()

    for i in range(num_threads):
        start_i = i * step
        end_i = (i + 1) * step
        thread = threading.Thread(target=calculate_sum, args=(start_i, end_i, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(results)
    print(f"Threading sum: {total_sum}")
    print(f"Execution time: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
