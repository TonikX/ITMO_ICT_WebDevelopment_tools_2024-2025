import multiprocessing
import time


def calculate_sum(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


def main():
    start_time = time.time()

    n = 10 ** 9
    num_processes = multiprocessing.cpu_count()
    chunk_size = n // num_processes

    tasks = []
    for i in range(num_processes):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i < num_processes - 1 else n
        tasks.append((start, end))

    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.starmap(calculate_sum, tasks)

    total_sum = sum(results)
    end_time = time.time()

    print(f"Итоговая сумма: {total_sum}")
    print(f"Время выполнения: {end_time - start_time:.2f} секунд")
    print(f"Количество процессов: {num_processes}")


if __name__ == "__main__":
    main()