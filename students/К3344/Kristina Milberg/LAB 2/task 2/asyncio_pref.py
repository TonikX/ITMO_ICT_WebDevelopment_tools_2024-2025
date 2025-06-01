import asyncio
import aiohttp
from bs4 import BeautifulSoup
from sqlmodel import SQLModel, create_engine, Session, select
import time
from models import Tag

# Настройка базы данных
DATABASE_URL = "postgresql://christina:123@localhost:5433/timemngmt_db"
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

# Список URL-ов
urls = [
    "https://quotes.toscrape.com/page/1/",
    "https://quotes.toscrape.com/page/2/",
    "https://quotes.toscrape.com/page/3/",
]

# Асинхронная функция загрузки и обработки страницы
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

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_and_save(session, url) for url in urls]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()
    print(f"\n Готово! Обработано {len(urls)} страниц за {round(end - start, 2)} сек.")
