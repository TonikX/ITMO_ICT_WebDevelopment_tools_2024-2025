from celery import Celery

celery_app = Celery(
    "lab3",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery_app.conf.task_routes = {
    "celery_worker.tasks.parse_url": {"queue": "default"},
}