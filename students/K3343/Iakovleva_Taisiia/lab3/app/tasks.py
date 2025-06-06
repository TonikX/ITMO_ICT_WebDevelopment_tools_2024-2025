from celery import Celery
import requests
from bs4 import BeautifulSoup
from db import save_parsed_page

celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@celery_app.task(bind=True)
def async_parse(self, url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "No title"
        save_parsed_page(url, title)
        return title
    except Exception as e:
        raise self.retry(exc=e, countdown=5, max_retries=3)
