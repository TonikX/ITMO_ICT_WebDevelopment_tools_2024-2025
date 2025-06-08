import threading
import time
from datetime import datetime


def calculate_partial_sum(start, end, result_list, index):
    result = sum(range(start, end))
    result_list[index] = result

def main():
    total = 10_000_000
    num_threads = 4
    step = total // num_threads
    threads = []
    results = [0] * num_threads

    start_time = time.perf_counter()

    for i in range(num_threads):
        a = i * step
        b = total if i == num_threads - 1 else (i + 1) * step
        t = threading.Thread(target=calculate_partial_sum, args=(a, b, results, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    total_sum = sum(results)
    elapsed = time.perf_counter() - start_time

    print(f"Threading sum = {total_sum}")
    print(f"Time: {elapsed:.2f} seconds")

    with open('sum_timings.csv', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()},threading,{elapsed:.6f}\n")

if __name__ == "__main__":
    main()