import asyncio
from celery import Celery

from config import settings
from parser import save_page

celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

@celery_app.task
def parse_url_task(url: str) -> dict:
    return asyncio.run(save_page(url, prefix="celery"))
