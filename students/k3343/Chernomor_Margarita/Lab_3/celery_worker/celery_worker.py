from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery = Celery(
    "parser_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["parser_app.tasks"]
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    task_default_queue='parser_queue',
    worker_max_tasks_per_child=1,
    worker_prefetch_multiplier=1
)
