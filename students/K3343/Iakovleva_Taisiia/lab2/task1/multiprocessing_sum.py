import multiprocessing
import time

def calculate_sum(start, end, queue):
    queue.put(sum(range(start, end + 1)))

def main():
    N = 10_000_000_000
    NUM_PROCESSES = 4
    step = N // NUM_PROCESSES
    queue = multiprocessing.Queue()
    processes = []

    t0 = time.time()
    for i in range(NUM_PROCESSES):
        start_range = i * step + 1
        end_range = (i + 1) * step if i < NUM_PROCESSES - 1 else N
        p = multiprocessing.Process(target=calculate_sum, args=(start_range, end_range, queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    total = sum(queue.get() for _ in range(NUM_PROCESSES))
    print("Multiprocessing result:", total)
    print("Time:", time.time() - t0, "seconds")

if __name__ == "__main__":
    main()
