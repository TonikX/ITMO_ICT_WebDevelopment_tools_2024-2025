import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

def partial_range_sum(start_index, end_index):
    return sum(range(start_index, end_index))

async def compute_total_sum():
    total_range = 1_000_000_000
    segment_size = total_range // 4

    def create_jobs():
        for idx in range(4):
            begin = idx * segment_size
            finish = (idx + 1) * segment_size if idx < 3 else total_range
            yield begin, finish

    with ThreadPoolExecutor(max_workers=4) as executor:
        loop = asyncio.get_running_loop()
        coroutines = [
            loop.run_in_executor(executor, partial_range_sum, start, end)
            for start, end in create_jobs()
        ]
        partial_sums = await asyncio.gather(*coroutines)

    return sum(partial_sums)

if __name__ == "__main__":
    start = time.time()
    final_sum = asyncio.run(compute_total_sum())
    print("Computed Sum:", final_sum)
    print("Duration:", round(time.time() - start, 2), "seconds")
