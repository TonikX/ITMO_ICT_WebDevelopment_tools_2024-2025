from .parser import grab_name
from celery_worker import celery_app

@celery_app.task
def parse_url(url: str):
    return grab_name(url)