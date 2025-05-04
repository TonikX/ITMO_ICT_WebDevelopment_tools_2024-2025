import os
import threading
from time import time
from typing import List
from bs4 import BeautifulSoup
import requests
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
    # Добавьте реальные URL
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


import re
from sqlmodel import Session
from bs4 import BeautifulSoup
import requests

from models import BookDefault, engine


def parse_books_from_html(url: str, genre: str):
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.find_all("tr")
    with Session(engine) as session:
        for row in rows:
            tds = row.find_all("td")
            if len(tds) < 1:
                continue

            first_td = tds[0]
            a_tag = first_td.find("a")
            font_tag = first_td.find("font")

            # Название книги
            if not a_tag:
                continue
            title = a_tag.text.strip().strip('«»')

            # Автор — текст до <a>
            author = a_tag.previous_sibling
            if author:
                author = author.strip()
            else:
                author = "Неизвестен"

            # Попытка извлечь год
            year = None
            if font_tag:
                match = re.search(r"(\d{4})", font_tag.text)
                if match:
                    year = int(match.group(1))

            # По умолчанию None → можно заменить на 0 или другой дефолт
            book_entry = BookDefault(
                title=title,
                author=author,
                genre=genre,
                published_year=year or 0
            )
            session.add(book_entry)

        session.commit()

print_lock = threading.Lock()

def thread_worker(url: str, genre: str):
    start_time = time()
    parse_books_from_html(url, genre)
    with print_lock:
        print(f"Parsed {url} in {time() - start_time:.2f}s")


def main():
    start_time = time()

    threads: List[threading.Thread] = []
    for url, genre in zip(URLS, GENRES):
        thread = threading.Thread(target=thread_worker, args=(url, genre))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    total_time = time() - start_time
    print(f"All threads completed in {total_time:.2f}s.")


if __name__ == "__main__":
    main()
