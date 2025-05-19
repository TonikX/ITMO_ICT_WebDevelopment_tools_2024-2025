from celery import Celery
from parser import parse_and_save

celery = Celery(
  'parser',
  broker='redis://redis:6379/0',
  backend='redis://redis:6379/1'
)

@celery.task(name='parse')
def parse_and_save_async(url: str):
  parse_and_save(url)