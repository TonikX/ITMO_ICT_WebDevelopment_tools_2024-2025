import multiprocessing as mp
from time import perf_counter


def compute_range_sum(range_start, range_end):
    total = 0
    for num in range(range_start, range_end + 1):
        total += num
    return total


def main():
    MAX_VALUE = 1_000_000_000
    PROCESS_COUNT = 4
    segment_size = MAX_VALUE // PROCESS_COUNT

    process_ranges = [
        (i * segment_size + 1,
         MAX_VALUE if i == PROCESS_COUNT - 1 else (i + 1) * segment_size)
        for i in range(PROCESS_COUNT)
    ]

    start_timer = perf_counter()
    with mp.Pool(processes=PROCESS_COUNT) as process_pool:
        partial_sums = process_pool.starmap(compute_range_sum, process_ranges)

    final_result = sum(partial_sums)
    elapsed_time = perf_counter() - start_timer

    print(f"Sum: {final_result}")
    print(f"Processing Duration: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()