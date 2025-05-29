import asyncio
import time
from celery import Celery
from parser import parse

celery = Celery('tasks', broker='redis://redis:6379', backend='redis://redis:6379')


@celery.task
def parse_celery(url: str):
    return asyncio.run(parse(url))