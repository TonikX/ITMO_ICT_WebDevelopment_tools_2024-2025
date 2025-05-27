import os
from celery import Celery
from celery.schedules import crontab
import requests

# Initialize Celery
celery_app = Celery(
    'parser_tasks',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'parse-every-hour': {
        'task': 'app.worker.celery_worker.parse_url_task',
        'schedule': crontab(minute=0, hour='*'),
        'args': ('https://react.dev/',),
    },
}

@celery_app.task(name='parse_url')
def parse_url_task(url: str):
    """
    Task to parse a given URL using the parser service
    """
    try:
        response = requests.post(
            'http://parser:8001/parse',
            json={'url': url}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {'error': str(e)} 