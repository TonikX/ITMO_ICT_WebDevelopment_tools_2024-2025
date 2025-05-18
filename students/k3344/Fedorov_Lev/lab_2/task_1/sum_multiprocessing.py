import multiprocessing
import time


def calculate_sum_part(start, end, result_queue, process_id):
    partial_sum = 0
    for i in range(start, end + 1):
        partial_sum += i
    result_queue.put((process_id, partial_sum))
    print(f"процесс {process_id}: вычислена сумма с {start} по {end} = {partial_sum}")


def calculate_sum_multiprocessing(n, num_processes=4):
    chunk_size = n // num_processes
    processes = []
    result_queue = multiprocessing.Queue()

    start_time = time.time()

    for i in range(num_processes):
        start = i * chunk_size + 1
        if i == num_processes - 1:
            end = n  # Последний процесс обрабатывает оставшиеся числа
        else:
            end = (i + 1) * chunk_size

        process = multiprocessing.Process(
            target=calculate_sum_part,
            args=(start, end, result_queue, i)
        )
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    results = []
    while not result_queue.empty():
        results.append(result_queue.get()[1])

    total_sum = sum(results)
    end_time = time.time()

    print(f"\nMultiprocessing сумма: {total_sum}")
    print(f"время затрачено: {end_time - start_time:.2f} seconds")
    return total_sum


if __name__ == "__main__":
    n = 10_000_000  # 10 миллионов
    calculate_sum_multiprocessing(n)
    # 0,17 sec