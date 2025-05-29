import os
import requests
from celery import Celery

app = Celery(
    "parser_tasks",
    broker=f"redis://{os.getenv('REDIS_HOST','redis')}:{os.getenv('REDIS_PORT','6379')}/0",
    backend=f"redis://{os.getenv('REDIS_HOST','redis')}:{os.getenv('REDIS_PORT','6379')}/0",
)

app.config_from_object("celery_app.celeryconfig")

@app.task(bind=True, name="parse_url")
def parse_url(self, url: str):
    try:
        resp = requests.post("http://parser:8001/parse", json={"url": url}, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10, max_retries=3)