import time

from implementations.async_impl import AsyncParser
from implementations.processes import ProcessParser
from implementations.threads import ThreadParser
from webpages.utils import ColorLog
from webpages.reset_db import reset_database


def pretty_print(name: str, duration: float, color_fn):
    print(color_fn(f"{name}:"))
    print(f"  Time taken: {duration:.2f} seconds")
    print("-" * 40)


def run_test(impl, urls, num_tasks):
    start = time.time()
    impl.parse_and_save_all(urls, num_tasks)
    end = time.time()
    return end - start


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
