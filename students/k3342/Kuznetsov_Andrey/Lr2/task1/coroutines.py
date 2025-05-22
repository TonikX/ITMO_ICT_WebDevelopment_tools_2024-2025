import asyncio
import time
import json


async def range_sum(args: tuple[int, int, int]) -> int:
    index, start, end = args
    print(f"-- Batch {index} started: summing from {start} to {end}")
    result = sum(range(start, end))
    print(f"-- Batch {index} finished")
    return result


async def big_sum(start: int, end: int, batches: int) -> int:
    steps_per_batch = (end - start) // batches
    ranges = [
        (i // steps_per_batch, i, min(i + steps_per_batch, end))
        for i in range(start, end, steps_per_batch)
    ]

    results = await asyncio.gather(*(range_sum(args) for args in ranges))
    return sum(results)


def test() -> None:
    test_batches = 5
    total, expected = asyncio.run(big_sum(1, 102, test_batches)), sum(range(1, 102))
    assert total == expected, f"Expected {expected}, got {total}"


if __name__ == "__main__":
    test()

    start_sum, end_sum, batches = 1, 1_000_000_000, 20_000
    print(f"Starting threaded sum from {start_sum} to {end_sum} in {batches} batches...")

    start_time = time.time()
    result = asyncio.run(big_sum(start_sum, end_sum + 1, batches))
    end_time = time.time()

    data: dict = {
        "batches": batches,
        "result": result,
        "duration_seconds": end_time - start_time
    }

    with open("coroutines.json", "w") as f:
        json.dump(data, f, indent=2)
