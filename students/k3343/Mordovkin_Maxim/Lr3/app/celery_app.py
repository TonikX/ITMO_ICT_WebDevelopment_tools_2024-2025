import os
from celery import Celery

REDIS_BROKER_URL = os.getenv("REDIS_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery = Celery(
    "parser_tasks",
    broker=REDIS_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)
