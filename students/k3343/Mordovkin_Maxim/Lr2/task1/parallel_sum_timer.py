import threading, time, asyncio
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

n = 10**8
k = 4

# threading
def sum_range_thread(args):
    start, end = args
    total = 0
    for i in range(start, end + 1):
        total += i
    return total

def calculate_sum_threading():
    chunk = n // k
    threads = []
    results = [0] * k

    def worker(idx, a, b):
        results[idx] = sum_range_thread((a, b))

    for i in range(k):
        a = i * chunk + 1
        b = (i + 1) * chunk if i < k - 1 else n
        t = threading.Thread(target=worker, args=(i, a, b))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return sum(results)

# multiprocessing
def calculate_sum_multiprocessing():
    chunk = n // k
    ranges = [
        (i * chunk + 1, (i + 1) * chunk if i < k - 1 else n)
        for i in range(k)
    ]
    with mp.Pool(processes=k) as pool:
        results = pool.map(sum_range_thread, ranges)
    return sum(results)

# asyncio
def sum_range_process(a, b):
    total = 0
    for i in range(a, b + 1):
        total += i
    return total

async def calculate_sum_async():
    chunk = n // k
    loop = asyncio.get_running_loop()
    tasks = []
    with ProcessPoolExecutor(max_workers=k) as executor:
        for i in range(k):
            a = i * chunk + 1
            b = (i + 1) * chunk if i < k - 1 else n
            tasks.append(loop.run_in_executor(executor, sum_range_process, a, b))
        results = await asyncio.gather(*tasks)
    return sum(results)


def run_threading():
    return calculate_sum_threading()

def run_multiprocessing():
    return calculate_sum_multiprocessing()

def run_asyncio():
    return asyncio.run(calculate_sum_async())

def main():
    methods = [
        ("threading", run_threading),
        ("multiprocessing", run_multiprocessing),
        ("asyncio", run_asyncio),
    ]

    summary = []
    for name, func in methods:
        start = time.perf_counter()
        total = func()
        duration = time.perf_counter() - start
        summary.append((name, duration, total))

    # Вывод результатов
    print(f"{'method':<25}{'time, с':<12}{'sum'}")
    print("-" * 50)
    for name, dur, tot in summary:
        print(f"{name:<25}{dur:<12.4f}{tot}")

if __name__ == "__main__":
    main()
