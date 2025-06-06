# app/celery_worker/celery_app.py
from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["app.celery_worker.tasks"]
)

celery_app.conf.task_routes = {
    "app.celery_worker.tasks.parse_url": {"queue": "parser"}
}