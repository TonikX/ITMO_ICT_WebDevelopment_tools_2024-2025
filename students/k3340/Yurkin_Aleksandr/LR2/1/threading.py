import threading
import time

def calculate_sum(start, end):
    return sum(range(start, end + 1))

def worker(start, end, results, index):
    results[index] = calculate_sum(start, end)

if __name__ == '__main__':
    N = 5000000000
    num_threads = 4
    chunk_size = N // num_threads
    threads = []
    results = [0] * num_threads

    start_time = time.time()
    for i in range(num_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_threads - 1 else N
        t = threading.Thread(target=worker, args=(start, end, results, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total = sum(results)
    end_time = time.time()

    print(f"Threading Total: {total}")
    print(f"Threading Time: {end_time - start_time:.2f} seconds")