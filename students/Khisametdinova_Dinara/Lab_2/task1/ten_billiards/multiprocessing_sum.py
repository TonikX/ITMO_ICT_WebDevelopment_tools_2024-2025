import multiprocessing
import time

def partial_sum(start, end, queue):
    n = end - start + 1
    queue.put((start + end) * n // 2)

def calculate_sum():
    total_start = 1
    total_end = 10_000_000_000_000
    num_processes = 8
    step = (total_end - total_start + 1) // num_processes

    processes = []
    queue = multiprocessing.Queue()

    for i in range(num_processes):
        start = total_start + i * step
        end = start + step - 1 if i != num_processes - 1 else total_end
        p = multiprocessing.Process(target=partial_sum, args=(start, end, queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    results = [queue.get() for _ in processes]
    return sum(results)

if __name__ == "__main__":
    start_time = time.time()
    total = calculate_sum()
    end_time = time.time()
    print(f"sum: {total}")
    print(f"time: {end_time - start_time:.2f} seconds")
