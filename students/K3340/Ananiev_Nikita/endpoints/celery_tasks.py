import os
from celery import Celery
from dotenv import load_dotenv
import requests

load_dotenv()

celery_app = Celery(
    __name__,
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL"),
)

@celery_app.task(name="parser_task")
def parser_task():
    response = requests.post(os.getenv("PARSER_URL"))
    return response.json()
