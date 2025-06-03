import asyncio
import aiohttp
from bs4 import BeautifulSoup
from sqlmodel import Session

from models import Page
from connection import engine


async def parse_and_save(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    print(f"Ошибка {response.status} для {url}")
                    return {"url": url, "title": None}

                html = await response.text()
                bs = BeautifulSoup(html, "html.parser")
                title = bs.title.string if bs.title else None

                # Сохраняем в БД
                with Session(engine) as db:
                    page = Page(url=url, title=title)
                    db.add(page)
                    db.commit()
                    db.refresh(page)

                return {"url": url, "title": title}
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {e}")
        return {"url": url, "title": None}


async def async_parse(urls: list[str]):
    results = await asyncio.gather(*[parse_and_save(url) for url in urls])
    return results