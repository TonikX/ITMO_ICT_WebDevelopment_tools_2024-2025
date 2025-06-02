import threading
import time

def calculate_partial_sum(start, end, result, index):
    result[index] = sum(range(start, end))

def main():
    total = 10**8
    num_threads = 4
    step = total // num_threads
    threads = []
    results = [0] * num_threads
    start_time = time.time()

    for i in range(num_threads):
        start_range = i * step
        end_range = (i + 1) * step if i != num_threads - 1 else total
        thread = threading.Thread(target=calculate_partial_sum, args=(start_range, end_range, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(results)
    print(f"Total Sum: {total_sum}")
    print(f"Time taken with threading: {time.time() - start_time} seconds")

if __name__ == "__main__":
    main()