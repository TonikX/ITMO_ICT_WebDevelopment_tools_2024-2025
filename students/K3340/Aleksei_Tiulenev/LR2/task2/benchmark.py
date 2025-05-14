import time

import matplotlib.pyplot as plt
from implementations.async_impl import AsyncParser
from implementations.processes import ProcessParser
from implementations.threads import ThreadParser
from reset_db import reset_database
from utils import ColorLog


def run_test(impl, urls, num_tasks):
    start = time.perf_counter()
    impl.parse_and_save_all(urls, num_tasks)
    end = time.perf_counter()
    return end - start


def benchmark(urls, num_tasks=8):
    implementations = [
        ("Threading", ThreadParser(), ColorLog.blue),
        ("Multiprocessing", ProcessParser(), ColorLog.green),
        ("Asyncio", AsyncParser(), ColorLog.yellow)
    ]

    results = {}

    for name, impl, _ in implementations:
        print(f"Running {name}...")
        reset_database()
        duration = run_test(impl, urls, num_tasks)
        results[name] = duration
        print(f"{name}: {duration:.2f} seconds")

    return results


if __name__ == "__main__":
    raw_urls = [
        "https://reactjs.dev",
        "https://vuejs.org",
        "https://angular.io",
        "https://svelte.dev",
        "https://preactjs.com",
        "https://emberjs.com",
        "https://backbonejs.org",
        "https://bootstrap-vue.org"
    ]

    url_multipliers = [1, 2, 5, 10]
    num_tasks = 8

    all_results = {"Threading": [], "Multiprocessing": [], "Asyncio": []}
    x_axis = []

    for multiplier in url_multipliers:
        urls = raw_urls * multiplier
        x_axis.append(len(urls))
        print(f"\nTesting with {len(urls)} URLs:")
        results = benchmark(urls, num_tasks)

        for name in all_results:
            all_results[name].append(results.get(name, 0))

    plt.figure(figsize=(10, 6))
    for name, times in all_results.items():
        plt.plot(x_axis, times, label=name)

    plt.xlabel("Number of URLs")
    plt.ylabel("Execution Time (seconds)")
    plt.title("Benchmark: Threading vs Multiprocessing vs Asyncio")
    plt.legend()
    plt.grid(True)
    plt.show()
