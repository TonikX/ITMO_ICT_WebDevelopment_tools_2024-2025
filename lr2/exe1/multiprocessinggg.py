import multiprocessing
import time

TOTAL = 1_000_000_000
NUM_PROCESSES = 4

def partial_sum(args):
    start, end = args
    return sum(range(start, end + 1))

def calculate_sum():
    chunk_size = TOTAL // NUM_PROCESSES
    ranges = []

    for i in range(NUM_PROCESSES):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != NUM_PROCESSES - 1 else TOTAL
        ranges.append((start, end))

    with multiprocessing.Pool(NUM_PROCESSES) as pool:
        results = pool.map(partial_sum, ranges)

    return sum(results)

if __name__ == "__main__":
    start_time = time.time()
    total_sum = calculate_sum()
    print(f"Multiprocessing: Сумма равна {total_sum}")
    print(f"Время выполнения: {time.time() - start_time:.4f} секунд")