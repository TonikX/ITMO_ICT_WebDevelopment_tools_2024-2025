from async_parse import main as async_main
from celery_app import celery_app
from multiprocessing_parse import main as mp_main
from threading_parse import main as threading_main


@celery_app.task(name = "parser.threading")
def parse_threading_task(urls):
    threading_main(urls)
    return "threading done"


@celery_app.task(name = "parser.multiprocessing")
def parse_mp_task(urls):
    mp_main(urls)
    return "multiprocessing done"


@celery_app.task(name = "parser.async")
def parse_async_task(urls):
    import asyncio
    return asyncio.run(async_main(urls))
