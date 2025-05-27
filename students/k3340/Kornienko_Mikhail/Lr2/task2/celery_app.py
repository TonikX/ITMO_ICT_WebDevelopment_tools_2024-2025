from celery import Celery

from parsing_async import run

REDIS_BROKER = "redis://redis:6379/0"
REDIS_BACKEND = "redis://redis:6379/1"

celery_app = Celery(
    "tasks",
    broker=REDIS_BROKER,
    backend=REDIS_BACKEND,
)

@celery_app.task(name="task.parse_urls")
def parse_urls_task(urls: list[str]) -> dict:
    elapsed_time = run(urls)
    return {"elapsed_sec": elapsed_time, "saved": len(urls)}