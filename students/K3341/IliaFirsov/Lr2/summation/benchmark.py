import time

import matplotlib.pyplot as plt
from implementations.async_impl import AsyncSummation
from implementations.processes import ProcessSummation
from implementations.threads import ThreadSummation
from utils import ColorLog


def run_test(impl, n, num_tasks):
    start = time.perf_counter()
    result = impl.calculate_sum(n, num_tasks)
    end = time.perf_counter()
    return end - start, result


def benchmark(n_list, num_tasks=8):
    implementations = [
        ("Threading", ThreadSummation(), ColorLog.blue),
        ("Multiprocessing", ProcessSummation(), ColorLog.green),
        ("Asyncio", AsyncSummation(), ColorLog.yellow)
    ]

    results = {name: [] for name, _, _ in implementations}

    for n in n_list:
        print(f"\nTesting for N = {n}")
        for name, impl, _ in implementations:
            duration, result = run_test(impl, n, num_tasks)
            print(f"{name}: {duration:.2f} sec (Result last 10 digits: {str(result)[-10:]})")
            results[name].append(duration)

    return results


if __name__ == "__main__":
    n_values = [
        1_000_000,
        5_000_000,
        10_000_000,
        50_000_000,
        100_000_000,
        1_000_000_000
    ]
    num_tasks = 8

    results = benchmark(n_values, num_tasks)

    plt.figure(figsize=(10, 6))
    for name, times in results.items():
        plt.plot(n_values, times, label=name)

    plt.xlabel("Верхняя граница суммирования (N)")
    plt.ylabel("Время выполнения (секунды)")
    plt.title("Бенчмарк суммирования: Threading vs Multiprocessing vs Asyncio")
    plt.legend()
    plt.grid(True)
    plt.show()
