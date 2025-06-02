from aiohttp import ClientSession
from bs4 import BeautifulSoup
from celery_app import celery_app
import asyncio


@celery_app.task(queue="parsing", name="parser.tasks.parse_url")
def parse_url(url: str) -> dict:
    """
    Этот таск выполняется в фоне Celery worker.
    Он делает HTTP-запрос, парсит страницу и возвращает результат.
    """

    async def _fetch_and_parse(u):
        async with ClientSession() as session:
            async with session.get(u, timeout=10) as response:
                if response.status != 200:
                    return {"error": f"Ошибка {response.status}"}
                html = await response.text()
                bs = BeautifulSoup(html, 'html.parser')

                title_tag = bs.find("h1", class_=lambda x: x and x.startswith('BookCard_book__title'))
                if not title_tag:
                    return {"error": "Не найден заголовок книги"}

                parent_divs = bs.find_all('div', class_=lambda x: x and x.startswith('Truncate_truncated'))
                if len(parent_divs) < 2:
                    return {"error": "Не найдены автор или описание"}

                title = title_tag.text.strip()
                author = parent_divs[0].text.strip()
                description = parent_divs[1].text.strip()

                return {
                    "title": title,
                    "author": author,
                    "description": description
                }

    return asyncio.run(_fetch_and_parse(url))
