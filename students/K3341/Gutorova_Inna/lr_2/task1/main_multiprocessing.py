import multiprocessing
import time


def calculate_sum(start_end):
    start, end = start_end
    return sum(range(start, end + 1))


def multiprocessing_sum():
    num_processes = 4
    total_numbers = 10 ** 6  # Уменьшено для демонстрации
    chunk_size = total_numbers // num_processes

    # Создаём диапазоны для каждого процесса
    ranges = [
        (i * chunk_size + 1,
         (i + 1) * chunk_size if i != num_processes - 1 else total_numbers)
        for i in range(num_processes)
    ]

    start_time = time.time()

    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(calculate_sum, ranges)

    total_sum = sum(results)
    end_time = time.time()

    print(f"Multiprocessing sum: {total_sum}, Time: {end_time - start_time:.4f} seconds")


if __name__ == '__main__':
    multiprocessing_sum()