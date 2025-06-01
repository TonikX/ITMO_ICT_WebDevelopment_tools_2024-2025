import multiprocessing
import time

N = 10_000_000
NUM_PROCESSES = 4


def calculate_sum(start, end):
    return sum(range(start, end))


def main():
    chunk_size = N // NUM_PROCESSES
    pool = multiprocessing.Pool(NUM_PROCESSES)
    tasks = []

    for i in range(NUM_PROCESSES):
        start = i * chunk_size
        end = N if i == NUM_PROCESSES - 1 else (i + 1) * chunk_size
        tasks.append((start, end))

    results = pool.starmap(calculate_sum, tasks)
    total = sum(results)
    print(f"Сумма: {total}")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    start_time = time.time()
    main()
    duration = time.time() - start_time
    print(f"Затрачено времени: {duration:.2f} секунд")
