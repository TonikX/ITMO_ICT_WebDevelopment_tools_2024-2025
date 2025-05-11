import asyncio
from time import perf_counter


def range_sum(start, end):
    total = 0
    for num in range(start, end + 1):
        total += num
    return total


async def execute_parallel():
    MAX_NUM = 1_000_000_000
    TASK_COUNT = 4
    segment_size = MAX_NUM // TASK_COUNT

    task_ranges = [
        (i * segment_size + 1,
         MAX_NUM if i == TASK_COUNT - 1 else (i + 1) * segment_size)
        for i in range(TASK_COUNT)
    ]

    start_timer = perf_counter()

    event_loop = asyncio.get_event_loop()
    tasks = [
        event_loop.run_in_executor(None, range_sum, start, end)
        for start, end in task_ranges
    ]

    partial_sums = await asyncio.gather(*tasks)

    final_sum = sum(partial_sums)
    elapsed_time = perf_counter() - start_timer

    print(f"Sum: {final_sum}")
    print(f"Execution Duration: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(execute_parallel())