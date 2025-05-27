import threading
import time

def calculate_sum(start, end, result, index):
    result[index] = sum(range(start, end + 1))

def main():
    total = 1000_000_000
    threads_num = 4
    chunk_size = total // threads_num
    results = [0] * threads_num
    threads = []

    start_time = time.time()

    for i in range(threads_num):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != threads_num - 1 else total
        thread = threading.Thread(
            target=calculate_sum,
            args=(start, end, results, i)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(results)
    end_time = time.time()

    print(f"Threading sum: {total_sum}")
    print(f"Time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
