from celery import Celery
import asyncio

from .parser import async_parse

celery_app = Celery(
    "parser",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@celery_app.task
def parse_url_task(url: str):
    count = asyncio.run(async_parse(url))
    return f"Добавлено книг: {count}"
