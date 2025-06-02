import multiprocessing
import time

sums = []
n = int(1e9)

def counter(x):
    return sum(range(x[0], n, x[1]))


def calculate_sums():
    process_count = 10
    with multiprocessing.Pool(processes=process_count) as pool:
        it = pool.imap_unordered(counter, [(i, process_count) for i in range(process_count)], chunksize=1)
        return sum(it)


if __name__ == '__main__':
    start = time.time()
    result = calculate_sums()
    print("Сумма:", result, "Время:", time.time() - start)