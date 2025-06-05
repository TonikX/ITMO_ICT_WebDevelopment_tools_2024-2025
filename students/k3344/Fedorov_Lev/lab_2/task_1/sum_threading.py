import threading
import time


def calculate_sum_part(start, end, result_dict, thread_id):
    """Вычисляет сумму чисел в заданном диапазоне"""
    partial_sum = 0
    for i in range(start, end + 1):
        partial_sum += i
    result_dict[thread_id] = partial_sum
    print(f"Thread {thread_id}: от {start} до {end} = {partial_sum}")


def calculate_sum_threading(n, num_threads=4):
    """Вычисляет сумму чисел от 1 до n используя threading"""
    chunk_size = n // num_threads
    threads = []
    result_dict = {}

    start_time = time.time()

    for i in range(num_threads):
        start = i * chunk_size + 1
        if i == num_threads - 1:
            end = n
        else:
            end = (i + 1) * chunk_size

        thread = threading.Thread(
            target=calculate_sum_part,
            args=(start, end, result_dict, i)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_sum = sum(result_dict.values())
    end_time = time.time()

    print(f"\nThreading общая сумма: {total_sum}")
    print(f"время затрачено: {end_time - start_time:.2f} seconds")
    return total_sum


if __name__ == "__main__":
    n = 10_000_000  # 10 миллионов
    calculate_sum_threading(n)
    # 0.29 sec