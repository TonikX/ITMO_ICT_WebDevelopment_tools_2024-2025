import asyncio
from celery import Celery
from Lr3.book_parser import BookParser

celery_app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

@celery_app.task
def parse_task(url: str):
    parser = BookParser(url=url)
    return asyncio.run(parser.run(count_of_workers=10))
