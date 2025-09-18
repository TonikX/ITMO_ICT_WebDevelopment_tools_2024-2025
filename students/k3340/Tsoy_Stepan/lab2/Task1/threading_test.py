import threading
import time

N = 10**9
NUM_WORKERS = 4
partial_sums = [0] * NUM_WORKERS

def calculate_sum(start, end, index):
    s = 0
    for i in range(start, end + 1):
        s += i
    partial_sums[index] = s

def main():
    step = N // NUM_WORKERS
    threads = []
    t0 = time.time()
    for i in range(NUM_WORKERS):
        start = i * step + 1
        end = (i + 1) * step if i < NUM_WORKERS - 1 else N
        th = threading.Thread(target=calculate_sum, args=(start, end, i))
        threads.append(th)
        th.start()

    for th in threads:
        th.join()
    total = sum(partial_sums)
    print("Threading total:", total)
    print("Elapsed:", time.time() - t0, "sec")

if __name__ == "__main__":
    main()
