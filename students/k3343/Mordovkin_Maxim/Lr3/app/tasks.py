import os
import requests
from app.celery_app import celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

PARSER_URL = os.getenv("PARSER_URL", "http://parser:8001/parse")

@celery.task(bind=True)
def parse_url_task(self, url: str):
    """
    Celery-задача: делает POST-запрос к микросервису-парсеру,
    возвращает результат JSON или выбрасывает исключение.
    """
    payload = {"url": url}
    try:
        response = requests.post(PARSER_URL, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Parsing succeeded for {url}: {data}")
        return data
    except requests.RequestException as e:
        # Можно пробросить ошибку, чтобы Celery пометил задачу неудачей
        logger.error(f"Ошибка при парсинге {url}: {e}")
        # Если нужно, можно сделать retry: self.retry(exc=e, countdown=10, max_retries=3)
        raise e
