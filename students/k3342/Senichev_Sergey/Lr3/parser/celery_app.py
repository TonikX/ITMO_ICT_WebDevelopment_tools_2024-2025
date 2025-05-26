import asyncio
import logging
from celery import Celery
from typing import List

from parsers.config import REDIS_URL
from parsers.async_parser import AsyncParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(
    "parser",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["celery_app"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)


@celery_app.task(bind=True)
def parse_repositories_task(self, repositories: List[str]):
    try:
        logger.info(f"Starting parsing task for repositories: {repositories}")
        
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": len(repositories), "status": "Starting..."}
        )
        
        parser = AsyncParser()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(parser.run(repositories))
        finally:
            loop.close()
        
        logger.info(f"Parsing task completed: {result}")
        
        return {
            "status": "SUCCESS",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error in parsing task: {str(e)}")
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise


@celery_app.task
def health_check():
    return {"status": "healthy", "worker": "parser-celery-worker"}


if __name__ == "__main__":
    celery_app.start() 