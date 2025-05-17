from celery import Celery
import os

celery_app = Celery(
    "ab_money",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
    include=["ab_money.celery_worker"]
)

@celery_app.task(name="ab_money.celery_worker.run_parser_task")
def run_parser_task(url: str):
    from task2.parse_asyncio import parse_sync
    titles = parse_sync(url)
    return titles
