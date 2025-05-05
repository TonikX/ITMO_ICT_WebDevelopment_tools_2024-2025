import asyncio
import time

async def compute_segment_sum(start_value, end_value):
    return sum(range(start_value, end_value + 1))

async def run_async_sum(total_limit=1000000000, segments=4):
    t0 = time.time()

    size = total_limit // segments
    boundaries = [
        (i * size + 1, (i + 1) * size if i < segments - 1 else total_limit)
        for i in range(segments)
    ]

    operations = [compute_segment_sum(a, b) for a, b in boundaries]
    segment_results = await asyncio.gather(*operations)

    overall = sum(segment_results)
    t1 = time.time()

    print(f"Sum: {overall}")
    print(f"Time: {t1 - t0:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(run_async_sum())
