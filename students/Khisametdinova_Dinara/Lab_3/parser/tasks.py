import asyncio

import aiohttp
from celery import Celery

from parser import parse_and_save_async

celery_app = Celery(
    "parser",
    broker="redis://redis:6379/0",
    backend='redis://redis:6379/0',
)


# celery_app.config_from_object("celery_config")

@celery_app.task
def run_parsing_task(req: dict):
    url = req["url"]
    table_name = req["table_name"]

    async def wrapper():
        async with aiohttp.ClientSession() as session:
            await parse_and_save_async(session, url, table_name)

    asyncio.run(wrapper())
