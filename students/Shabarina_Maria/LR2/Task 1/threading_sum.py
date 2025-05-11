import threading
import time


def partial_sum(start, end, result, index):
    result[index] = sum(range(start, end))


def calculate_sum():
    num_threads = 4
    maximum = 10**9
    step = maximum // num_threads
    threads = []
    results = [0] * num_threads
    for i in range(num_threads):
        start = i * step + 1
        if i != num_threads - 1:
            end = (i + 1) * step + 1
        else:
            end = maximum + 1
        t = threading.Thread(target=partial_sum, args=(start, end, results, i))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return sum(results)


if __name__ == "__main__":
    start_time = time.time()
    total = calculate_sum()
    duration = time.time() - start_time
    print("Threading")
    print("Итоговая сумма:", total)
    print("Время выполнения:", time.time() - start_time, "сек")
