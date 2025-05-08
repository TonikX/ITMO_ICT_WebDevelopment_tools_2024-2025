import requests
from bs4 import BeautifulSoup
import random
import time

urls = {
    "Современная зарубежная литература": "https://www.livelib.ru/genre/Современная-зарубежная-литература",
    "Зарубежная классика": "https://www.livelib.ru/genre/Зарубежная-классика",
    "Зарубежные детективы": "https://www.livelib.ru/genre/Зарубежные-детективы",
    "Фэнтези": "https://www.livelib.ru/genre/Фэнтези",
    "Приключения": "https://www.livelib.ru/genre/Приключения"
}

USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
        "Mozilla/5.0 (X11; Linux x86_64)..."
    ]


def clean_description(text: str) -> str:
    text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    cutoff_phrases = ["Развернуть", "развернуть"]
    for phrase in cutoff_phrases:
        if phrase in text:
            return text.split(phrase)[0].strip() + "..."
    return text.strip()


def parse_books_from_genre_page(url, genre_name, max_books=3):
    books = []

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "...",
        "Accept-Language": "...",
        "Referer": "..."
    }

    session = requests.Session()
    response = session.get(url, headers=headers, timeout=10)
    time.sleep(random.uniform(1.5, 3.0))
    soup = BeautifulSoup(response.text, "html.parser")
    book_items = soup.select("li[class*=book-item__item]")[:max_books]

    for item in book_items:
        try:
            title_tag = item.find("a", class_="book-item__title")
            author_tag = item.find("a", class_="book-item__author")
            if not title_tag or not author_tag:
                raise ValueError("Не найдены теги с названием или автором")


            title = title_tag.text.strip()
            author = author_tag.text.strip()

            info_table = item.find("table", class_="book-item-edition")
            rows = info_table.find_all("tr") if info_table else []
            isbn, published_in, publisher = None, None, None

            for row in rows:
                label = row.find("td", class_="book-item-edition__col1").text.strip()
                value = row.find_all("td")[1].text.strip()
                if label == "ISBN:":
                    isbn = value
                elif label == "Год издания:":
                    published_in = int(value)
                elif label == "Издательство:":
                    publisher = value

            publisher = publisher.replace('\xa0', ' ').replace('\r', '').replace('\n', '').strip()
            publisher = ', '.join(part.strip() for part in publisher.split(','))

            description_div = item.find("div", class_="book-item__text")
            description = description_div.get_text(separator="\n").strip() if description_div else None
            description = clean_description(description)

            book_data = {
                "title": title,
                "author": author,
                "genre": genre_name,
                "isbn": isbn,
                "published_in": published_in,
                "publisher": publisher,
                "description": description
            }

            books.append(book_data)
        except Exception as e:
            print("Ошибка при парсинге книги:", e)
            continue

    return books


all_books = []
for genre, url in urls.items():
    books = parse_books_from_genre_page(url, genre)
    all_books.extend(books)

for book in all_books:
    print(book)
