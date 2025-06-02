import threading
import time
import json


def range_sum(start: int, end: int, result: list[int], index: int) -> None:
    result[index] = sum(range(start, end))


def big_sum(start: int, end: int, batches: int, result: list[int]) -> None:
    threads: list[threading.Thread] = []
    steps_per_batch: int = (end - start) // batches

    for i, batch_start in enumerate(range(start, end, steps_per_batch)):
        batch_end: int = min(batch_start + steps_per_batch, end)
        thread: threading.Thread = threading.Thread(
            target=range_sum,
            args=(batch_start, batch_end, result, i)
        )
        threads.append(thread)
        thread.start()
        print(f"-- Batch {i} is started: summing from {batch_start} to {batch_end}")

    for i, thread in enumerate(threads):
        thread.join()
        print(f"-- Batch {i} is finished")


def test() -> None:
    test_batches: int = 5
    test_result_list: list[int] = [0] * (test_batches + 1)
    big_sum(1, 102, test_batches, test_result_list)

    total, expected = sum(test_result_list), sum(range(1, 102))
    assert total == expected, f"Expected {expected}, got {total}"


if __name__ == "__main__":
    test()

    start_sum, end_sum, batches = 1, 1_000_000_000, 100
    print(f"Starting sum from {start_sum} to {end_sum} in {batches} batches...")

    result_list: list[int] = [0] * batches
    start_time = time.time()
    big_sum(start_sum, end_sum + 1, batches, result_list)
    end_time = time.time()

    data: dict = {
        "batches": batches,
        "result": sum(result_list),
        "duration_seconds": end_time - start_time
    }

    with open("threads.json", "w") as f:
        json.dump(data, f, indent=2)
