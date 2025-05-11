from multiprocessing import Pool
import time


def part_sum(args):
    start, end = args
    return sum(range(start, end))


def calculate_sum_multiprocessing(n, num_processes):
    step = n // num_processes
    ranges = [(i * step + 1, n + 1 if i == num_processes - 1 else (i + 1) * step + 1) for i in range(num_processes)]
    with Pool(processes=num_processes) as pool:
        results = pool.map(part_sum, ranges)
    return sum(results)


if __name__ == "__main__":
    n = 10 ** 9
    start_time = time.time()
    total = calculate_sum_multiprocessing(n, 5)
    print("Сумма:", total)
    print("Время выполнения:", time.time() - start_time, "сек")
