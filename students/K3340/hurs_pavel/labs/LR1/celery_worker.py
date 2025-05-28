from celery import Celery
import os
import requests
from celery.schedules import crontab

# Initialize Celery
celery = Celery(
    'time_manager',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
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
        'task': 'celery_worker.parse_url',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
        'args': (['https://reactjs.org', 'https://vuejs.org'],)
    },
}

@celery.task(name='parse_url')
def parse_url(urls):
    """Parse URLs using the parser service."""
    parser_url = os.getenv('PARSER_URL', 'http://localhost:8001')
    results = []
    
    for url in urls:
        try:
            # Make request to parser service
            response = requests.post(
                f"{parser_url}/parse",
                json={"url": url}
            )
            response.raise_for_status()
            results.append(response.json())
        except requests.RequestException as e:
            results.append({"error": str(e), "url": url})
    
    return results