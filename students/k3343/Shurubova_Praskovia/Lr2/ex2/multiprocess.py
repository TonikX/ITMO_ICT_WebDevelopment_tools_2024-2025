import multiprocessing
import time
import requests
from parser import parse_genre_page
from db import init_db
from sqlmodel import Session

URLS = [
    "https://www.livelib.ru/genre/%D0%9A%D0%BB%D0%B0%D1%81%D1%81%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B0%D1%8F-%D0%BB%D0%B8%D1%82%D0%B5%D1%80%D0%B0%D1%82%D1%83%D1%80%D0%B0",
    "https://www.livelib.ru/genre/%D0%97%D0%B0%D1%80%D1%83%D0%B1%D0%B5%D0%B6%D0%BD%D1%8B%D0%B5-%D0%B4%D0%B5%D1%82%D0%B5%D0%BA%D1%82%D0%B8%D0%B2%D1%8B"
]


engine = init_db()


def parse_and_save(url: str):
    try:

        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)

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


def multiprocessing_main():
    start = time.time()
    processes = []

    for url in URLS:
        proc = multiprocessing.Process(target=parse_and_save, args=(url,))
        processes.append(proc)
        proc.start()

    for proc in processes:
        proc.join()

    print(f"Multiprocessing выполнен за {time.time() - start:.2f} секунд")


if __name__ == "__main__":
    multiprocessing_main()
