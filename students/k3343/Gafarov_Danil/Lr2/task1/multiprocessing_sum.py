import multiprocessing
import time

TOTAL = 1_000_000_000
PROCESSES = 4

def calculate_sum(args):
    start, end = args
    partial_sum = 0
    for i in range(start, end + 1):
        partial_sum += i
    return partial_sum

def main():
    step = TOTAL // PROCESSES
    pool_args = []

    start_time = time.time()

    for i in range(PROCESSES):
        start = i * step + 1
        end = (i + 1) * step if i != PROCESSES - 1 else TOTAL
        pool_args.append((start, end))

    with multiprocessing.Pool(PROCESSES) as pool:
        results = pool.map(calculate_sum, pool_args)

    total_sum = sum(results)
    end_time = time.time()

    print(f"Multiprocessing: Сумма = {total_sum}, время = {end_time - start_time:.4f} сек")

if __name__ == "__main__":
    main()