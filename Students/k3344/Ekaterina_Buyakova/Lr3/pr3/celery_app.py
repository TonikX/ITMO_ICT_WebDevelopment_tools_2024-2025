import requests
from bs4 import BeautifulSoup
from celery import Celery

from core import settings
from core.database import SessionLocal
from models.parsed_sites import ParsedSites

celery_app = Celery(
    "parser_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    timezone='Europe/Moscow',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    max_retries=5,
)


@celery_app.task()
def parse_and_save(url) -> None:
    with SessionLocal() as session:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else 'No title'

            url = ParsedSites(url=url, title=title)
            session.add(url)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
