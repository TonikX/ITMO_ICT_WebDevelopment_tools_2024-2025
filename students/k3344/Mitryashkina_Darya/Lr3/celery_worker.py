from celery import Celery
from asgiref.sync import async_to_sync
from task2.parse_asyncio import main
import os
from dotenv import load_dotenv

load_dotenv()
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

celery_app = Celery(
    "parser",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

@celery_app.task(name="parse")
def parse(url: str):
    async_to_sync(main)(url)