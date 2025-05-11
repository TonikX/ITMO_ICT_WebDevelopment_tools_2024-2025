from threading import Thread
from time import perf_counter


def sum_range(start, end):
    total = 0
    for num in range(start, end + 1):
        total += num
    return total


def process_chunk(start, end, results, position):
    results[position] = sum_range(start, end)


def main():
    MAX_NUM = 1_000_000_000
    THREAD_COUNT = 4
    segment_size = MAX_NUM // THREAD_COUNT

    result_array = [0] * THREAD_COUNT
    thread_pool = []

    start_timer = perf_counter()

    for idx in range(THREAD_COUNT):
        range_start = idx * segment_size + 1
        range_end = MAX_NUM if idx == THREAD_COUNT - 1 else (idx + 1) * segment_size
        thread = Thread(target=process_chunk, args=(range_start, range_end, result_array, idx))
        thread_pool.append(thread)
        thread.start()

    for thread in thread_pool:
        thread.join()

    final_sum = sum(result_array)
    elapsed_time = perf_counter() - start_timer

    print(f"Sum: {final_sum}")
    print(f"Execution Time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()