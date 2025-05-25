import time
import multiprocessing

MAX_VALUE = 10**9
PROCESS_COUNT = 10

def partial_sum(x):
    return sum(range(x[0], MAX_VALUE, x[1]))

def calculate_sums():
    with multiprocessing.Pool(processes=PROCESS_COUNT) as pool:
        parts = pool.imap_unordered(
            partial_sum, 
            [(i, PROCESS_COUNT) for i in range(PROCESS_COUNT)], 
            chunksize=1
        )
        return sum(parts)

if __name__ == '__main__':
    start = time.time()
    result = calculate_sums()
    duration = time.time() - start
    print(f"Итоговая сумма:", result)
    print(f"Затрачено времени: {duration:.3f} сек")