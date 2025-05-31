import os

from celery import Celery
import httpx

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

PARSER_SERVICE_URL = os.getenv("PARSER_SERVICE_URL")

@celery_app.task
def parse_books_task(url: str, genre: str):
    payload = {"url": url, "genre": genre}
    try:
        response = httpx.post(PARSER_SERVICE_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}
