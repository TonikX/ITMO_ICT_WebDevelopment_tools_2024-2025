import multiprocessing

import time

N = 1_000_000_000
PROCESSES = 4

def calculate_sum(start, end, queue):
    queue.put(sum(range(start, end)))

def run_multiprocessing():
    processes = []
    queue = multiprocessing.Queue()
    step = N // PROCESSES
    start_time = time.time()

    for i in range(PROCESSES):
        start = i * step
        end = N if i == PROCESSES - 1 else (i + 1) * step
        p = multiprocessing.Process(target=calculate_sum, args=(start, end, queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    total = sum(queue.get() for _ in processes)
    print("Multiprocessing Total:", total)
    print("Multiprocessing Time:", time.time() - start_time)
if __name__ == "__main__":
    run_multiprocessing()
