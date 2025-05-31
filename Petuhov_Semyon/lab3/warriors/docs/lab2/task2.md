# Offer
Задача 2. Параллельный парсинг веб-страниц с сохранением в базу данных
Были написаны 3 различные реализации 

threading
```python
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


```
Результат:
Parsed https://fantlab.ru/bygenre?wg34=on&disauthors=0&lang_id=&gend=&form= in 0.07s
Parsed https://fantlab.ru/bygenre?wg31=on&disauthors=0&lang_id=&gend=&form= in 0.07s
Parsed https://fantlab.ru/bygenre?wg225=on&disauthors=0&lang_id=&gend=&form= in 0.34s
Parsed https://fantlab.ru/bygenre?wg35=on&disauthors=0&lang_id=&gend=&form= in 0.35s
Parsed https://fantlab.ru/bygenre?wg37=on&disauthors=0&lang_id=&gend=&form= in 0.36s
Parsed https://fantlab.ru/bygenre?wg1=on&wg2=on&disauthors=0&lang_id=&gend=&form= in 0.60s
Parsed https://fantlab.ru/bygenre?wg2=on&wg19=on&disauthors=0&lang_id=&gend=&form= in 0.61s
Parsed https://fantlab.ru/bygenre?wg160=on&disauthors=0&lang_id=&gend=&form= in 0.63s
All threads completed in 0.63s.


async
```python
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


```

Результат:
Parsed https://fantlab.ru/bygenre?wg37=on&disauthors=0&lang_id=&gend=&form= in 0.07s
Parsed https://fantlab.ru/bygenre?wg31=on&disauthors=0&lang_id=&gend=&form= in 0.08s
Parsed https://fantlab.ru/bygenre?wg35=on&disauthors=0&lang_id=&gend=&form= in 0.28s
Parsed https://fantlab.ru/bygenre?wg225=on&disauthors=0&lang_id=&gend=&form= in 0.36s
Parsed https://fantlab.ru/bygenre?wg34=on&disauthors=0&lang_id=&gend=&form= in 0.43s
Parsed https://fantlab.ru/bygenre?wg2=on&wg19=on&disauthors=0&lang_id=&gend=&form= in 0.51s
Parsed https://fantlab.ru/bygenre?wg160=on&disauthors=0&lang_id=&gend=&form= in 0.62s
Parsed https://fantlab.ru/bygenre?wg1=on&wg2=on&disauthors=0&lang_id=&gend=&form= in 0.69s
All async tasks completed in 0.69s.

multiprocessing
```python
import os
import re
from time import time
from typing import List
from bs4 import BeautifulSoup
import requests
from sqlmodel import Session
from multiprocessing import Process, Lock

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

            if not a_tag:
                continue

            title = a_tag.text.strip().strip('«»')
            author = a_tag.previous_sibling
            if author:
                author = author.strip()
            else:
                author = "Неизвестен"

            year = None
            if font_tag:
                match = re.search(r"(\d{4})", font_tag.text)
                if match:
                    year = int(match.group(1))

            book_entry = BookDefault(
                title=title,
                author=author,
                genre=genre,
                published_year=year or 0
            )
            session.add(book_entry)

        session.commit()


def process_worker(url: str, genre: str, lock: Lock):
    start_time = time()
    parse_books_from_html(url, genre)
    with lock:
        print(f"Parsed {url} in {time() - start_time:.2f}s")


def main():
    start_time = time()

    lock = Lock()
    processes: List[Process] = []

    for url, genre in zip(URLS, GENRES):
        process = Process(target=process_worker, args=(url, genre, lock))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    total_time = time() - start_time
    print(f"All processes completed in {total_time:.2f}s.")


if __name__ == "__main__":
    main()


```

Результаты:
Parsed https://fantlab.ru/bygenre?wg37=on&disauthors=0&lang_id=&gend=&form= in 0.06s
Parsed https://fantlab.ru/bygenre?wg225=on&disauthors=0&lang_id=&gend=&form= in 0.06s
Parsed https://fantlab.ru/bygenre?wg35=on&disauthors=0&lang_id=&gend=&form= in 0.25s
Parsed https://fantlab.ru/bygenre?wg31=on&disauthors=0&lang_id=&gend=&form= in 0.31s
Parsed https://fantlab.ru/bygenre?wg34=on&disauthors=0&lang_id=&gend=&form= in 0.29s
Parsed https://fantlab.ru/bygenre?wg2=on&wg19=on&disauthors=0&lang_id=&gend=&form= in 0.49s
Parsed https://fantlab.ru/bygenre?wg1=on&wg2=on&disauthors=0&lang_id=&gend=&form= in 0.52s
Parsed https://fantlab.ru/bygenre?wg160=on&disauthors=0&lang_id=&gend=&form= in 0.53s
All processes completed in 1.50s.


Общие результаты:
Threading - 0.63 секунды


Async - 0.69 секунд


Multiprocessing - 1.50 секунды



В этой задаче multithreading не дал прироста скорости, а наоборот замедлил выполнения, т.к. это задача не CPU-bound,
в ней преобладает  IO-bound 
