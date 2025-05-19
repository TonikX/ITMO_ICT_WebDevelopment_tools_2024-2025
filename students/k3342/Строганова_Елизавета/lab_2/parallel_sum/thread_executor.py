

import asyncio
from concurrent.futures import ThreadPoolExecutor
from .base import get_ranges, sum_range

async def threadpool_sum(total: int, workers: int) -> int:
    ranges = get_ranges(total, workers)
    loop = asyncio.get_running_loop()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        tasks = [
            loop.run_in_executor(executor, sum_range, start, end)
            for start, end in ranges
        ]
        results = await asyncio.gather(*tasks)

    return sum(results)
