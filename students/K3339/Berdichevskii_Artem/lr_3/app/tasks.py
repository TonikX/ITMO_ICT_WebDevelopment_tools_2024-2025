from celery import Celery
from app.parser import fetch_page_content
import os

celery_app = Celery(
    "tasks",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
)

@celery_app.task
def parse_url_task(url: str):
    content = fetch_page_content(url)
    return f"Parsed {len(content)} characters"