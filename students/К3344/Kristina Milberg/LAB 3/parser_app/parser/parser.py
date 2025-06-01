import asyncio
import aiohttp
from bs4 import BeautifulSoup
from sqlmodel import SQLModel, create_engine, Session, select
from parser.models import Tag
import os

DATABASE_URL = os.getenv("DB_URL")
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

async def fetch_and_save(session: aiohttp.ClientSession, url: str):
    try:
        print(f"[Async] Парсим: {url}")
        async with session.get(url, timeout=10) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            tag_elements = soup.select("a.tag")

            with Session(engine) as db_session:
                for tag_el in tag_elements:
                    tag_name = tag_el.text.strip()
                    if tag_name:
                        exists = db_session.exec(select(Tag).where(Tag.name == tag_name)).first()
                        if not exists:
                            db_session.add(Tag(name=tag_name))
                            print(f"[Async] Сохранили тег: {tag_name}")
                db_session.commit()
    except Exception as e:
        print(f"[Async] Ошибка при обработке {url}: {e}")

async def run_parser(urls: list[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_and_save(session, url) for url in urls]
        await asyncio.gather(*tasks)
