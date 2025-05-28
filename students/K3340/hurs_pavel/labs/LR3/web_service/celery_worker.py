from celery import Celery
import os
import requests
from celery.schedules import crontab

# Initialize Celery
celery = Celery(
    'web_service',
    broker=os.getenv('REDIS_URL', 'redis://redis:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://redis:6379/0')
)

# Configure Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Configure periodic tasks
celery.conf.beat_schedule = {
    'parse-daily-urls': {
        'task': 'celery_worker.parse_urls',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
        'args': (['https://reactjs.org', 'https://vuejs.org'],)
    },
}

@celery.task(name='parse_urls')
def parse_urls(urls):
    """Parse URLs using the parser service."""
    parser_url = os.getenv('PARSER_URL', 'http://parser:8001')
    results = []
    
    for url in urls:
        try:
            response = requests.post(
                f"{parser_url}/parse",
                json={"url": url}
            )
            response.raise_for_status()
            results.append(response.json())
        except requests.RequestException as e:
            results.append({"error": str(e), "url": url})
    
    return results