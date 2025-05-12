from multiprocessing import Pool
import time


def calculate_sum(sumrange: tuple[int, int]):
    start, end = sumrange
    subsum = 0
    for i in range(start, end + 1):
        subsum += i
    return subsum


if __name__ == "__main__":
    NUM_PROCESSES = 10
    START = 1
    END = 10**9

    step = END // NUM_PROCESSES
    ranges = []
    for i in range(NUM_PROCESSES):
        cur_start = START + i * step
        cur_end = START + (i + 1) * step - 1
        ranges.append((cur_start, cur_end))

    start = time.time()
    with Pool(processes=NUM_PROCESSES) as pool:
        subsums = pool.map(calculate_sum, ranges)
    fullsum = sum(subsums)
    print("Final sum=", fullsum)
    print("Done in", time.time() - start, "seconds")

"""
NUM_PROCESSES = 10

Final sum= 500000000500000000
Done in 5.467380046844482 seconds
"""

"""
NUM_PROCESSES = 1

Final sum= 500000000500000000
Done in 34.41407608985901 seconds
"""
