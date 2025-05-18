from app.task_logic import run_parser_logic
from app.celery_part import celery


@celery.task
def run_parser_task(urls: list[str]):
    return run_parser_logic(urls)
