import threading
import time
import requests
from parser import parse_genre_page
from db import init_db
from sqlmodel import Session


URLS = [
    "https://www.livelib.ru/genre/Наука-и-образование",
    "https://www.livelib.ru/genre/Детские-книги"
]

engine = init_db()


def parse_and_save(url: str):
    try:
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0'
        }, timeout=10)

        if response.status_code != 200:
            print(f"Не удалось загрузить {url}, статус: {response.status_code}")
            return

        html = response.text
        books = parse_genre_page(html)

        valid_books = [b for b in books if b.name and b.author and b.year and b.publisher]

        if valid_books:
            with Session(engine) as session:
                session.add_all(valid_books)
                session.commit()
            print(f"Сохранено {len(valid_books)} книг с {url}")
        else:
            print(f"Нет валидных книг на странице {url}")
    except Exception as e:
        print(f"Ошибка при обработке {url}: {e}")


def threading_main():
    start = time.perf_counter()
    threads = []

    for url in URLS:
        thread = threading.Thread(target=parse_and_save, args=(url,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print(f"\nThreading выполнен за {time.perf_counter() - start:.2f} секунд.")


if __name__ == "__main__":
    threading_main()
