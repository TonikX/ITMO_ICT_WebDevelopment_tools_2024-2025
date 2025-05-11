import multiprocessing
import time

TOTAL = 1000000000
NUM_PROCESSES = 4


def calculate_sum(start, end, queue):
    total = 0
    for i in range(start, end):
        total += i
    queue.put(total)


def main():
    processes = []
    queue = multiprocessing.Queue()
    chunk = TOTAL // NUM_PROCESSES
    start_time = time.time()

    for i in range(NUM_PROCESSES):
        start = i * chunk + 1
        end = (i + 1) * chunk + 1 if i != NUM_PROCESSES - 1 else TOTAL + 1
        p = multiprocessing.Process(target=calculate_sum, args=(start, end, queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    total_sum = 0
    while not queue.empty():
        total_sum += queue.get()

    print("Total:", total_sum)
    print("Time (multiprocessing):", time.time() - start_time)

if __name__ == "__main__":
    main()

# Time (multiprocessing): 12.324779272079468