from celery import Celery
import asyncio
from app.async_parser import process_asset

celery_app = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery_app.conf.task_serializer = 'json'
celery_app.conf.accept_content = ['json']
celery_app.conf.result_serializer = 'json'
celery_app.conf.timezone = 'UTC'
celery_app.conf.task_routes = {
    "app.tasks.run_parser_task": {"queue": "parser"}
}

@celery_app.task(name='parse_asset')
def parse_asset(asset):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(process_asset(asset))
        else:
            asyncio.run(process_asset(asset))
        return {"message": f"Parsing completed for {asset['name']}"}
    except Exception as e:
        return {"error": str(e)}