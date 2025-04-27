import asyncio
import threading_parse, multiprocessing_parse, async_parse
from connection import init_db


def run_all():
    init_db()

    urls = [
        "https://habr.com/ru/users/dalerank/",
        "https://habr.com/ru/users/ntsaplin/",
        "https://habr.com/ru/users/techno_mot/"
    ]

    print("\nThreading")
    threading_parse.main(urls)

    print("\nMultiprocessing")
    multiprocessing_parse.main(urls)

    print("\nAsync")
    asyncio.run(async_parse.main(urls))


if __name__ == "__main__":
    run_all()
