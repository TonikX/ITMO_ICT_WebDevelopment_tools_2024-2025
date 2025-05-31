import multiprocessing
import time


def calculate_sum(start, end, queue):
    queue.put(sum(range(start, end)))


def main():
    total = 10_000_000
    num_processes = 4
    step = total // num_processes
    processes = []
    queue = multiprocessing.Queue()

    start_time = time.time()

    for i in range(num_processes):
        start_i = i * step
        end_i = (i + 1) * step
        p = multiprocessing.Process(target=calculate_sum, args=(start_i, end_i, queue))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    total_sum = 0
    while not queue.empty():
        total_sum += queue.get()

    print(f"Multiprocessing sum: {total_sum}")
    print(f"Execution time: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
