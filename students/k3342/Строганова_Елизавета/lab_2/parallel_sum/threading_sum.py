
import threading
from .base import get_ranges, sum_range

def threaded_sum(total: int, workers: int) -> int:
    ranges = get_ranges(total, workers)
    results = [0] * workers
    threads = []

    def task(i: int, start: int, end: int):
        results[i] = sum_range(start, end)

    for i, (start, end) in enumerate(ranges):
        t = threading.Thread(target=task, args=(i, start, end))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return sum(results)
