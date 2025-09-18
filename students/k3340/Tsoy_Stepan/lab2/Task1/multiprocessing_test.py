import multiprocessing
import time

N = 10**9
NUM_WORKERS = 4

def calculate_sum(start, end):
    s = 0
    for i in range(start, end + 1):
        s += i
    return s

def main():
    step = N // NUM_WORKERS
    tasks = []
    with multiprocessing.Pool(processes=NUM_WORKERS) as pool:
        for i in range(NUM_WORKERS):
            start = i * step + 1
            end = (i + 1) * step if i < NUM_WORKERS - 1 else N
            tasks.append(pool.apply_async(calculate_sum, (start, end)))
        t0 = time.time()
        results = [task.get() for task in tasks]
    total = sum(results)
    print("Multiprocessing total:", total)
    print("Elapsed:", time.time() - t0, "sec")

if __name__ == "__main__":
    main()
