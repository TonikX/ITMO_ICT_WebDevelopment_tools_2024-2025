import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

celery = Celery(
    "task",
    broker=REDIS_URL,
    backend=REDIS_URL
)

from app.task import run_parser_task

celery.task(name="app.task.run_parser_task")(run_parser_task)
