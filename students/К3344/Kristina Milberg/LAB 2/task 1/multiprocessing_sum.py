import multiprocessing
import time

N = 1_000_000_000
PROCESSES = 4

def calculate_sum(start, end, queue):
    queue.put(sum(range(start, end)))

def main():
    start_time = time.time()
    step = N // PROCESSES
    queue = multiprocessing.Queue()
    processes = []

    for i in range(PROCESSES):
        start_i = i * step
        end_i = N if i == PROCESSES - 1 else (i + 1) * step
        p = multiprocessing.Process(target=calculate_sum, args=(start_i, end_i, queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    total = sum(queue.get() for _ in processes)
    print("Multiprocessing Result:", total)
    print("Time:", time.time() - start_time)

if __name__ == "__main__":
    main()
