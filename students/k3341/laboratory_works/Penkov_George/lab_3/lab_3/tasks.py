import asyncio
from celery import Celery
from parser import parse_and_save

celery_app = Celery(
    "worker", broker="redis://redis:6379/0", backend="redis://redis:6379/0"
)


@celery_app.task
def parse_and_save_task(url: str):
    return asyncio.run(parse_and_save(url))
