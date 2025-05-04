import re
import asyncio
from typing import List
from time import time
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from sqlmodel import Session

from models import BookDefault, engine


URLS = [
    "https://fantlab.ru/bygenre?wg1=on&wg2=on&disauthors=0&lang_id=&gend=&form=",
    "https://fantlab.ru/bygenre?wg2=on&wg19=on&disauthors=0&lang_id=&gend=&form=",
    "https://fantlab.ru/bygenre?wg31=on&disauthors=0&lang_id=&gend=&form=",
    "https://fantlab.ru/bygenre?wg34=on&disauthors=0&lang_id=&gend=&form=",
    "https://fantlab.ru/bygenre?wg35=on&disauthors=0&lang_id=&gend=&form=",
    "https://fantlab.ru/bygenre?wg225=on&disauthors=0&lang_id=&gend=&form=",
    "https://fantlab.ru/bygenre?wg37=on&disauthors=0&lang_id=&gend=&form=",
    "https://fantlab.ru/bygenre?wg160=on&disauthors=0&lang_id=&gend=&form=",
]
GENRES = [
    "sci-fi",
    "fantasy",
    "horror",
    "detective",
    "action",
    "thriller",
    "historical proze",
    "realism",
]


async def fetch_html(session: ClientSession, url: str) -> str:
    async with session.get(url) as response:
        response.encoding = 'utf-8'
        return await response.text()


def parse_and_store_books(html: str, genre: str):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")

    with Session(engine) as session:
        for row in rows:
            tds = row.find_all("td")
            if not tds:
                continue

            first_td = tds[0]
            a_tag = first_td.find("a")
            font_tag = first_td.find("font")

            if not a_tag:
                continue

            title = a_tag.text.strip().strip('«»')
            author = a_tag.previous_sibling.strip() if a_tag.previous_sibling else "Неизвестен"

            year = 0
            if font_tag:
                match = re.search(r"(\d{4})", font_tag.text)
                if match:
                    year = int(match.group(1))

            book_entry = BookDefault(
                title=title,
                author=author,
                genre=genre,
                published_year=year
            )
            session.add(book_entry)
        session.commit()


async def async_worker(session: ClientSession, url: str, genre: str):
    from time import time
    start_time = time()
    html = await fetch_html(session, url)
    parse_and_store_books(html, genre)
    print(f"Parsed {url} in {time() - start_time:.2f}s")


async def main():
    start_time = time()

    async with ClientSession() as session:
        tasks = [
            async_worker(session, url, genre)
            for url, genre in zip(URLS, GENRES)
        ]
        await asyncio.gather(*tasks)

    print(f"All async tasks completed in {time() - start_time:.2f}s.")


if __name__ == "__main__":
    asyncio.run(main())
