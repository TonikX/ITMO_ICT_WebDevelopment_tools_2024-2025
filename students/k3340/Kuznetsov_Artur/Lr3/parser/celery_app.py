import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv(dotenv_path = "parser/.env")

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

celery_app = Celery(
    "parser_tasks",
    broker = CELERY_BROKER_URL,
    backend = CELERY_RESULT_BACKEND,
    include=["tasks"]
)
