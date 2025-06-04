import asyncio
import aiohttp
from bs4 import BeautifulSoup

from celery_worker import celery_app
from connection import get_session
from models import Page


@celery_app.task
def parse_and_save_task(url: str):
    asyncio.run(parse(url))


async def parse(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()

    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title else "No title"

    with get_session() as session:
        page = Page(url=url, title=title)
        session.merge(page)
        session.commit()
