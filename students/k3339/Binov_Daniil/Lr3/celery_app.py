from celery import Celery

app = Celery('time_manager',
             broker='redis://redis:6379/0',
             backend='redis://redis:6379/0',
             include=['celery_tasks'])

app.conf.update(
    result_expires=3600,
)