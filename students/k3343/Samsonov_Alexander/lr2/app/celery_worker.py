from app.task_manager.scheduler import beat_schedule
from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["app.task_manager.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule=beat_schedule,
)
