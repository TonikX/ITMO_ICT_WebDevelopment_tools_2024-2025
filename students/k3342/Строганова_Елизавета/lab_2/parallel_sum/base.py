
from typing import List, Tuple

def get_ranges(total: int, workers: int) -> List[Tuple[int, int]]:
    chunk = total // workers
    return [
        (i * chunk, (i + 1) * chunk if i < workers - 1 else total)
        for i in range(workers)
    ]

def sum_range(start: int, end: int) -> int:
    return sum(range(start, end))
