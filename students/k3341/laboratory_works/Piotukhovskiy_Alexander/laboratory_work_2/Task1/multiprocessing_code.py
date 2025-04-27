import multiprocessing
import time

N = 10**9
PARTS = 5


def calculate_range(start: int, end: int) -> int:
    return sum(range(start, end))


def calculate_sum_multiprocessing() -> int:
    chunk_size = N // PARTS
    ranges = []
    for i in range(PARTS):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size + 1
        ranges.append((start, end))

    with multiprocessing.Pool(PARTS) as pool:
        results = pool.starmap(calculate_range, ranges)

    return sum(results)


if __name__ == "__main__":
    t0 = time.time()
    result_multiprocessing = calculate_sum_multiprocessing()
    t1 = time.time()
    print(f"Multiprocessing result: {result_multiprocessing}, time: {t1 - t0:.2f}s")