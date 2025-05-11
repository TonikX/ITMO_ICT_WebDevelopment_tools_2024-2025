import threading
import time


def part_sum(start, end, result, index):
    result[index] = sum(range(start, end))


def calculate_sum_threading(n, num_threads):
    step = n // num_threads
    threads = []
    result = [0] * num_threads
    for i in range(num_threads):
        start = i * step + 1
        end = n + 1 if i == num_threads - 1 else (i + 1) * step + 1
        t = threading.Thread(target=part_sum, args=(start, end, result, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return sum(result)


if __name__ == "__main__":
    n = 10 ** 9
    start_time = time.time()
    total = calculate_sum_threading(n, 5)
    print("Сумма:", total)
    print("Время выполнения:", time.time() - start_time, "сек")
