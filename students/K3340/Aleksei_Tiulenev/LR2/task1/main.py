import time

from implementations.async_impl import AsyncSummation
from implementations.processes import ProcessSummation
from implementations.threads import ThreadSummation
from utils import ColorLog


def pretty_print(name: str, duration: float, result: int, color_fn):
    print(color_fn(f"{name}:"))
    print(f"  Time taken: {duration:.2f} seconds")
    print(f"  Result (last 10 digits): {str(result)[-10:]}")
    print("-" * 40)


def run_test(impl, n, num_tasks):
    start = time.time()
    result = impl.calculate_sum(n, num_tasks)
    end = time.time()
    return end - start, result


if __name__ == "__main__":
    n = 1_000_000_000
    num_tasks = 8

    implementations = [
        ("Threading", ThreadSummation(), ColorLog.blue),
        ("Multiprocessing", ProcessSummation(), ColorLog.green),
        ("Asyncio", AsyncSummation(), ColorLog.yellow)
    ]

    for name, impl, color_fn in implementations:
        duration, result = run_test(impl, n, num_tasks)
        pretty_print(name, duration, result, color_fn)
