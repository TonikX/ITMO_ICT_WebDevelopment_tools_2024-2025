from celery import Celery
import asyncio
from celery.result import AsyncResult

from main import parse_link

celery_app = Celery(
    "parser",
    broker="redis://lr5-redis-1:6379/0",
    backend="redis://lr5-redis-1:6379/0"
)

@celery_app.task
def parse_url_task(url: str):
    return parse_link(url)