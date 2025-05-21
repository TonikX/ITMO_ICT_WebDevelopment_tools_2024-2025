import threading
import time
from bs4 import BeautifulSoup
import requests
import os

from sqlalchemy import text
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


n = 4
urls = [
    "https://www.litres.ru/popular/",
    "https://www.litres.ru/new/",
]

urls = urls + [f"https://www.litres.ru/{selection}/?page={page}" for selection in ["popular", "new"] for page in range(1, ((n - 2) // 2) + 1)]


def parse(url: str, results: list):
    print(url)
    load_dotenv()
    db_url = os.getenv('DB_ADMIN').replace('+asyncpg', '')
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)

    response = requests.get(url)
    if response is None:
        print("Страница не найдена!")

    soup = BeautifulSoup(response.text, features="html.parser")

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
        print("INSERT INTO book (title, author) VALUES (:title, :author)", {"title": title, "author": author})

    session = Session()
    result = session.execute(text("SELECT * from public.book"))
    print(len(result.scalar()))

if __name__ == "__main__":

    start_time = time.perf_counter()
    results = []
    threads: list[threading.Thread] = []

    for url in urls:
        thread = threading.Thread(target=parse, args=(url, results))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print(len(results))

    print(f"Время: {time.perf_counter() - start_time}")