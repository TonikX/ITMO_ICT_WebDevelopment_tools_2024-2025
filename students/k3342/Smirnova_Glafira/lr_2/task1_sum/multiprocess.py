import multiprocessing
import time


def calculate_partial_sum(start, end):
    return sum(range(start, end + 1))


def main():
    n = 1000000000
    num_processes = multiprocessing.cpu_count()  # все доступные ядра
    chunk_size = n // num_processes

    print(f"Вычисление суммы чисел от 1 до {n:,}")
    print(f"Используется {num_processes} процессов...")

    ranges = []
    for i in range(num_processes):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_processes - 1 else n
        ranges.append((start, end))

    start_time = time.time()

    # пул процессов
    with multiprocessing.Pool(processes=num_processes) as pool:
        partial_sums = pool.starmap(calculate_partial_sum, ranges)
        total_sum = sum(partial_sums)

    end_time = time.time()

    expected_sum = n * (n + 1) // 2
    is_correct = total_sum == expected_sum

    print("\nРезультат:")
    print(f"Вычисленная сумма: {total_sum}")
    print(f"Ожидаемая сумма:   {expected_sum}")
    print(f"Совпадает: {'Да' if is_correct else 'Нет'}")
    print(f"Время выполнения: {end_time - start_time:.6f} секунд")


if __name__ == "__main__":
    main()

# Используется 4 процессов...
# Время выполнения: 18.060662 секунд
