import multiprocessing as mp
import time

n = 10**13
k = 4

def sum_range(args):
    """
    Принимает кортеж (start, end) и считает сумму всех чисел в этом диапазоне
    :param args: (start, end) - начало и конец поддиапазона
    :return: частичную сумму
    """
    start, end = args
    s = 0
    for i in range(start, end + 1):
        s += i
    return s

def calculate_sum():
    chunk = n // k
    ranges = []
    for i in range(k):
        a = i * chunk + 1
        b = (i + 1) * chunk if i < k - 1 else n
        ranges.append((a, b))

    start_time = time.perf_counter()
    with mp.Pool(processes=k) as pool:
        results = pool.map(sum_range, ranges)
    s = sum(results)
    elapsed = time.perf_counter() - start_time
    print(f"[multiprocessing] sum = {s}, time = {elapsed:.2f}s")

if __name__ == "__main__":
    calculate_sum()
