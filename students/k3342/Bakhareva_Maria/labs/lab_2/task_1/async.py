import asyncio
import time

async def calculate_sum(start: int, end: int) -> int:
    return (end - start + 1) * (start + end) // 2

async def compute_aggregate():
    max_value = 10_000_000_000_000
    segments = 4
    segment_size = max_value // segments

    tasks = []
    for segment in range(segments):
        begin = segment * segment_size + 1
        finish = (segment + 1) * segment_size if segment < segments - 1 else max_value
        tasks.append(asyncio.create_task(calculate_sum(begin, finish)))

    results = await asyncio.gather(*tasks)
    return sum(results)

if __name__ == "__main__":
    start_clock = time.perf_counter()
    overall_sum = asyncio.run(compute_aggregate())
    end_clock = time.perf_counter()

    print(f"Async: result = {overall_sum}, duration: {end_clock - start_clock:.6f} seconds")