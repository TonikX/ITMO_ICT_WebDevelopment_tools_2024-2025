from app.celery_worker import celery_app
from app.async_parser import run_parser
import asyncio


@celery_app.task(name="app.tasks.run_parser_task")
def run_parser_task():
    print("Парсинг начат через Celery")
    asyncio.run(run_parser())
    print("Парсинг завершён через Celery")
