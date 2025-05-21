from celery import Celery
import asyncio
from run import extract_user_links 
import async_

celery_app = Celery(
    "parser",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

@celery_app.task(name="parse_from_url")
def parse_from_url(url: str):
    asyncio.run(run_async(url))

async def run_async(url: str):
    user_urls = await extract_user_links(url)
    await async_.main(user_urls)
