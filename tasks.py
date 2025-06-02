from celery import Celery
import os
from dotenv import load_dotenv
from lab2.task2.async_parser import process_jobs
import asyncio

load_dotenv()

# Initialize Celery
celery_app = Celery(
    'tasks',
    broker=os.getenv('REDIS_URL', 'redis://redis:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://redis:6379/0')
)

# Optional configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(bind=True)
def parse_task(self, start_id: int, end_id: int):
    """
    Celery task for parsing jobs
    """
    # Update task state to STARTED
    self.update_state(state='STARTED')
    
    try:
        # Run the async parser
        results = asyncio.run(process_jobs(start_id, end_id))
        return {
            'status': 'success',
            'message': 'Parsing completed',
            'results': results
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        } 