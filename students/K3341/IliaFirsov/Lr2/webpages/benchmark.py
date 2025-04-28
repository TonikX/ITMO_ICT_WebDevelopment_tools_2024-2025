import time

import matplotlib.pyplot as plt
from implementations.async_impl import AsyncParser
from implementations.processes import ProcessParser
from implementations.threads import ThreadParser
from webpages.reset_db import reset_database
from webpages.utils import ColorLog


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
        "https://www.python.org",
        "https://www.djangoproject.com",
        "https://flask.palletsprojects.com",
        "https://fastapi.tiangolo.com",
        "https://docs.aiohttp.org",
        "https://www.asyncio.org",
        "https://realpython.com",
        "https://www.sqlalchemy.org"
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

    plt.xlabel("Количество URL")
    plt.ylabel("Время выполнения (секунды)")
    plt.title("Бенчмарк Threading vs Multiprocessing vs Asyncio")
    plt.legend()
    plt.grid(True)
    plt.show()
