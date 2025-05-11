import threading
import time

TOTAL = 1000000000
NUM_THREADS = 4
results = [0] * NUM_THREADS


def calculate_sum(start, end, index):
    total = 0
    for i in range(start, end):
        total += i
    results[index] = total


def main():
    threads = []
    chunk = TOTAL // NUM_THREADS
    start_time = time.time()

    for i in range(NUM_THREADS):
        start = i * chunk + 1
        end = (i + 1) * chunk + 1 if i != NUM_THREADS - 1 else TOTAL + 1
        t = threading.Thread(target=calculate_sum, args=(start, end, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total_sum = sum(results)
    expected = TOTAL * (TOTAL + 1) // 2
    print("Total:", total_sum)
    print("Expected:", expected)
    print("Time (threading):", time.time() - start_time)

if __name__ == "__main__":
    main()

# Time (threading): 43.961265563964844