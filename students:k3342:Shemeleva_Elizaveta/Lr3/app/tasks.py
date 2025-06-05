import asyncio
from .celery_app import celery
from .parser_service import ParserService

@celery.task(name="app.tasks.parse_task")
def parse_task(url: str):
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(
        ParserService.parse_url(url, save_to_db=True)
    )
    return result
