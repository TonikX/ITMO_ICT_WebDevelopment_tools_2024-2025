import threading
import time

TOTAL = 1_000_000_000
THREADS = 4

def calculate_sum(start, end, result, index):
    partial_sum = 0
    for i in range(start, end + 1):
        partial_sum += i
    result[index] = partial_sum

def main():
    step = TOTAL // THREADS
    threads = []
    result = [0] * THREADS

    start_time = time.time()

    for i in range(THREADS):
        start = i * step + 1
        end = (i + 1) * step if i != THREADS - 1 else TOTAL
        thread = threading.Thread(target=calculate_sum, args=(start, end, result, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(result)
    end_time = time.time()

    print(f"Threading: Сумма = {total_sum}, время = {end_time - start_time:.4f} сек")

if __name__ == "__main__":
    main()