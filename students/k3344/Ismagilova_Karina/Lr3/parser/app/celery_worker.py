import asyncio
import inspect

from celery import Celery
from .parser import parse_and_save_tours

celery_app = Celery(
    'trip',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0',
)

@celery_app.task
def parse_url_task(url: str):
    print(f"Using parse_and_save from module: {parse_and_save_tours.__module__}")
    print(f"Function signature: {inspect.signature(parse_and_save_tours)}")
    result = asyncio.run(parse_and_save_tours(url))
    return f"Добавлено {result} новых туров"