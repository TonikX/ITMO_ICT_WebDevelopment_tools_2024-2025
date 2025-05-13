import threading, time

n = 10**13
k = 4

def sum_range(start: int, end: int, res: dict, ind: int):
    """
    Вычисляет сумму чисел в диапазоне от start до end и сохраняет результат в словаре
    :param start: начало диапазона
    :param end: конец диапазона
    :param res: dict для хранения частичных результатов
    :param ind: ключ в dict, по которому будет сохранён результат
    """
    s = 0
    for i in range(start, end + 1):
        s += i
    res[ind] = s

def calculate_sum():
    chunk = n // k
    threads = []
    results = {}

    start_time = time.perf_counter()
    for i in range(k):
        a = i * chunk + 1
        b = (i + 1) * chunk if i < k - 1 else n
        t = threading.Thread(target=sum_range, args=(a, b, results, i))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    s = sum(results.values())
    elapsed = time.perf_counter() - start_time
    print(f"[threading] sum = {s}, time = {elapsed:.2f}s")

if __name__ == "__main__":
    calculate_sum()
