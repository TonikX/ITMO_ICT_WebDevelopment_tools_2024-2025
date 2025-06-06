import threading
import time

def calculate_sum(start, end, results, index):
    results[index] = sum(range(start, end + 1))

def main():
    N = 10_000_000_000  
    NUM_THREADS = 4
    step = N // NUM_THREADS
    results = [0] * NUM_THREADS
    threads = []

    t0 = time.time()
    for i in range(NUM_THREADS):
        start_range = i * step + 1
        end_range = (i + 1) * step if i < NUM_THREADS - 1 else N
        t = threading.Thread(target=calculate_sum, args=(start_range, end_range, results, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total = sum(results)
    print("Threading result:", total)
    print("Time:", time.time() - t0, "seconds")

if __name__ == "__main__":
    main()
