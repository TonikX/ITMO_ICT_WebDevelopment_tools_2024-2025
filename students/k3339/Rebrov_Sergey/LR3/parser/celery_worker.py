from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["tasks"],
)

celery_app.conf.task_routes = {
    "tasks.parse_and_save_task": {"queue": "parser"},
}
