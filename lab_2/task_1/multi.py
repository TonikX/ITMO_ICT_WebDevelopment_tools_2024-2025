import multiprocessing as mp
import time

def calculate_sum_range(args):
    start, end = args
    total = 0
    for i in range(start, end + 1):
        total += i
    return total

def main():
    N = 100_000_000
    num_procs = mp.cpu_count() 
    chunk = N // num_procs

    ranges = []
    for i in range(num_procs):
        s = i * chunk + 1
        e = (i + 1) * chunk if i < num_procs - 1 else N
        ranges.append((s, e))

    t0 = time.time()
    with mp.Pool(processes=num_procs) as pool:
        results = pool.map(calculate_sum_range, ranges)
    total = sum(results)
    t1 = time.time()

    print(f"Multiprocessing: сумма = {total}, время = {t1 - t0:.3f} сек")

if __name__ == "__main__":
    main()
