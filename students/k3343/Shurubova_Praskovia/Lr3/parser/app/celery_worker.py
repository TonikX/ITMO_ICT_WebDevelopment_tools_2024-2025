import asyncio
from celery import Celery
from .parser import parse_and_save_book

celery_app = Celery(
    'bookcrossing',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0',
)

@celery_app.task
def parse_url_task(url: str):
    result = asyncio.run(parse_and_save_book(url))
    return f"Добавлено {result} новых книг"
