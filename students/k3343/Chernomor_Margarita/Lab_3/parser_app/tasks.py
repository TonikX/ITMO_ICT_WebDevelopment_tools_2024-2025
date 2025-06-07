from celery import shared_task
from .db import parse_and_save
from .parser import urls


@shared_task
def parse_books_task():
    for genre, url in urls.items():
        parse_and_save(url, genre, 3)
    return {"status": "success", "message": "Parsing completed"}
