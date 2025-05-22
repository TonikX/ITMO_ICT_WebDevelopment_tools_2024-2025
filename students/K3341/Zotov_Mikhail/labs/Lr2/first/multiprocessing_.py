import multiprocessing
import time


def calculate_sum(a, b, results):
    s = 0
    for i in range(a, b + 1):
        s += i
    results.append(s)


def main(n, count_of_processes):
    start_time = time.time()
    size = n // count_of_processes
    manager = multiprocessing.Manager()
    results = manager.list()
    processes = []
    for i in range(count_of_processes):
        a = i * size + 1
        b = (i + 1) * size if (i + 1) * size < n else n
        process = multiprocessing.Process(target=calculate_sum, args=(a, b, results))
        processes.append(process)
        process.start()
    for process in processes:
        process.join()
    total = sum(results)
    print('Result:', total)
    end_time = time.time()
    print('Total time:', end_time - start_time)


if __name__ == '__main__':
    main(10 ** 9, 10)
