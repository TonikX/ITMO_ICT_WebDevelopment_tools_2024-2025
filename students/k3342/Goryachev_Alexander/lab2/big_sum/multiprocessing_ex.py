import multiprocessing
import time

MAX_NUMBER = 1_000_000_000
NUM_PROCESSES = multiprocessing.cpu_count()

def partial_sum(start, end):
    return sum(range(start, end + 1))

def calculate_sum():
    step = MAX_NUMBER // NUM_PROCESSES
    ranges = []

    for i in range(NUM_PROCESSES):
        start = i * step + 1
        end = (i + 1) * step if i < NUM_PROCESSES - 1 else MAX_NUMBER
        ranges.append((start, end))

    with multiprocessing.Pool(processes=NUM_PROCESSES) as pool:
        results = pool.starmap(partial_sum, ranges)

    return sum(results)

if __name__ == "__main__":
    start_time = time.time()
    result = calculate_sum()
    end_time = time.time()

    print(f"Сумма от 1 до {MAX_NUMBER}: {result}")
    print(f"Время выполнения: {end_time - start_time:.2f} секунд")