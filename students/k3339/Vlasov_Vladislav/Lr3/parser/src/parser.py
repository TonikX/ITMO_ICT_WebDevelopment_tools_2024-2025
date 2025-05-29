import time
from bs4 import BeautifulSoup
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv

import aiohttp

async def parse(url: str):
    print(url)
    time.sleep(7)
    results = []
    load_dotenv()
    db_url = os.getenv('DB_ADMIN')
    engine = create_async_engine(db_url)
    AsyncSession = async_sessionmaker(bind=engine)

    async with aiohttp.ClientSession() as http_session:
        async with http_session.get(url) as response:
            soup = BeautifulSoup(await response.text(), features="html.parser")

            books = soup.find_all("div", { "class": "ArtInfo_info__BgoQR"} )

            for book in books:
                try:
                    title = book.find("a", { "data-testid": "art__title"}).text
                except:
                    title = None
                try:
                    author = book.find("a", { "data-testid": "art__authorName"}).text
                except:
                    author = None

                results.append((title, author))
                #print("INSERT INTO book (title, author) VALUES (:title, :author)", {"title": title, "author": author}) 

                session = AsyncSession()
                await session.execute(text("INSERT INTO book (title, author, condition, status) VALUES (:title, :author, 'normal', 'available')"), {"title": title, "author": author})
                await session.commit()
                await session.close()
    

    await engine.dispose()

    return results