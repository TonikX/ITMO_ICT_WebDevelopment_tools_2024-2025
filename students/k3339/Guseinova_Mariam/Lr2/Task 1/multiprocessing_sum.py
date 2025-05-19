import multiprocessing
import time

def calculate_sum(start, end, queue):
    queue.put(sum(range(start, end)))

if __name__ == "__main__":
    start_time = time.time()
    total = 1_000_000_000
    num_processes = 4
    step = total // num_processes
    processes = []
    queue = multiprocessing.Queue()

    for i in range(num_processes):
        p = multiprocessing.Process(target=calculate_sum, args=(i * step, (i + 1) * step, queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    result = sum(queue.get() for _ in range(num_processes))
    print(f"Total sum: {result}")
    print(f"Execution time (multiprocessing): {time.time() - start_time:.2f} seconds")
