import time
import multiprocessing

from implementations.async_impl import AsyncParser
from implementations.processes import ProcessParser
from implementations.threads import ThreadParser
from utils import ColorLog
from reset_db import reset_database

multiprocessing.set_start_method('spawn', force=True)


def pretty_print(name: str, duration: float, color_fn):
    print(color_fn(f"{name}:"))
    print(f"  время: {duration:.2f} сек")
    print("-" * 40)


def run_test(impl, urls, num_tasks):
    start = time.time()
    impl.parse_and_save_all(urls, num_tasks)
    end = time.time()
    return end - start


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
    urls = []
    for i in range(5):
        urls.extend(raw_urls)

    num_tasks = 8

    implementations = [
        ("Threading", ThreadParser(), ColorLog.blue),
        ("Multiprocessing", ProcessParser(), ColorLog.green),
        ("Asyncio", AsyncParser(), ColorLog.yellow)
    ]

    reset_database()

    for name, impl, color_fn in implementations:
        duration = run_test(impl, urls, num_tasks)
        pretty_print(name, duration, color_fn)
