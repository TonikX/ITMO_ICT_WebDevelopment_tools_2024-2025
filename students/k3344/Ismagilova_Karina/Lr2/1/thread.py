import threading
import time

def calculate_partial_sum(start, end, result, index):
    result[index] = sum(range(start, end))

def main():
    start_time = time.time()
    n_threads = 5
    total = 1000000000
    chunk_size = total // n_threads
    threads = []
    results = [0] * n_threads

    for i in range(n_threads):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size + 1
        t = threading.Thread(target=calculate_partial_sum, args=(start, end, results, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total_sum = sum(results)
    print("Total sum:", total_sum)
    print("Time:", time.time() - start_time)
    # Time: 31.38943386077881

if __name__ == "__main__":
    main()
