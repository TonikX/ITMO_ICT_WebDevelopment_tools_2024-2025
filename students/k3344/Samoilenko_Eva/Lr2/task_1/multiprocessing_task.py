import multiprocessing
import time


def calculate_sum(start, end, result, index):
    result[index] = sum(range(start, end + 1))


def multiprocessing_sum(N, num_processes=4):
    chunk_size = N // num_processes  # Разбиваем N на части
    processes = []
    manager = multiprocessing.Manager()
    results = manager.list([0] * num_processes)

    start_time = time.time()

    for i in range(num_processes):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size if i != num_processes - 1 else N
        # Создаем процесс для каждой части
        process = multiprocessing.Process(target=calculate_sum, args=(start, end, results, i))
        processes.append(process)
        process.start()  # Запускаем процессы параллельно

    for process in processes:
        process.join()  # Ожидаем завершения всех процессов

    total = sum(results)

    end_time = time.time()
    print(f"Multiprocessing sum: {total}, Time: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    # N = 100_000_000
    N = 1_000_000_000
    multiprocessing_sum(N)

# 1 Multiprocessing sum: 5000000050000000, Time: 1.0373 seconds
# 2 Multiprocessing sum: 500000000500000000, Time: 6.9930 seconds
