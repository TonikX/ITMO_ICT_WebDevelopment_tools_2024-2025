import os
from celery import Celery
import requests

REDIS_BROKER = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
REDIS_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery_app = Celery("parser", broker=REDIS_BROKER, backend=REDIS_BACKEND)

@celery_app.task
def parse_url(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    html = resp.text

    title = html.split('<title itemprop="headline">')[1].split('</title>')[0]
    wealth = html.split('profile-info__item-value">$')[1].split('B</div>')[0]
    wealth = wealth.replace('.', '') if wealth else "0"
    return {"title": title, "wealth": wealth}
