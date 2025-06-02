from celery import Celery

celery_app = Celery(
    "parser",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
    include=["tasks"],
)

celery_app.conf.task_routes = {
    "parser.tasks.parse_url": {"queue": "parsing"},
}
