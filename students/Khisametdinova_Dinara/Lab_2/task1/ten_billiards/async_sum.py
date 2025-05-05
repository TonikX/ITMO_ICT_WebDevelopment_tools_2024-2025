import asyncio
import time

async def segment_sum(start, end):
    count = end - start + 1
    return (start + end) * count // 2

async def async_arithmetic_sum(total=10_000_000_000, parts=8):
    start_time = time.time()
    chunk = total // parts

    tasks = []
    for i in range(parts):
        seg_start = i * chunk + 1
        seg_end = (i + 1) * chunk if i < parts - 1 else total
        tasks.append(segment_sum(seg_start, seg_end))

    results = await asyncio.gather(*tasks)
    final_sum = sum(results)
    end_time = time.time()

    print(f"Sum: {final_sum}")
    print(f"Time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(async_arithmetic_sum())
