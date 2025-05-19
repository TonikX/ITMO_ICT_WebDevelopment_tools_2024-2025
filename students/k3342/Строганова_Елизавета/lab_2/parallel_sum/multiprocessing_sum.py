
from multiprocessing import Pool, freeze_support
from .base import get_ranges, sum_range

def multiprocess_sum(total: int, workers: int) -> int:
    freeze_support()
    ranges = get_ranges(total, workers)

    with Pool(processes=workers) as pool:
        results = pool.starmap(sum_range, ranges)

    return sum(results)
