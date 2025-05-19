import requests
from bs4 import BeautifulSoup
import random
import time

# Словарь жанров и соответствующих URL на Goodreads
genres_links = {
    "Science Fiction": "https://www.goodreads.com/shelf/show/science-fiction",
    "Mystery": "https://www.goodreads.com/shelf/show/mystery",
    "Historical Fiction": "https://www.goodreads.com/shelf/show/historical-fiction",
    "Romance": "https://www.goodreads.com/shelf/show/romance",
    "Young Adult": "https://www.goodreads.com/shelf/show/young-adult"
}

# Список User-Agent для имитации различных браузеров
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (X11; Linux x86_64)..."
]

def clean_text(text: str) -> str:
    """
    Очистка текста от лишних пробелов и символов новой строки.
    """
    return ' '.join(text.strip().split())

def parse_books_from_genre_page(url, genre_name, max_books=3):
    books = []

    headers = {
        "User-Agent": random.choice(USER_AGENTS)
    }

    session = requests.Session()
    response = session.get(url, headers=headers, timeout=10)
    time.sleep(random.uniform(1.5, 3.0))
    soup = BeautifulSoup(response.text, "html.parser")

    # Поиск контейнеров с книгами
    book_items = soup.select("div.elementList")[:max_books]

    for item in book_items:
        try:
            title_tag = item.find("a", class_="bookTitle")
            author_tag = item.find("a", class_="authorName")
            if not title_tag or not author_tag:
                raise ValueError("Не найдены теги с названием или автором")

            title = clean_text(title_tag.text)
            author = clean_text(author_tag.text)

            # Goodreads не предоставляет ISBN, издательство и год издания на этой странице
            isbn = None
            published_in = None
            publisher = None

            # Описание также отсутствует на этой странице
            description = None

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
for genre, url in genres_links.items():
    books = parse_books_from_genre_page(url, genre)
    all_books.extend(books)

for book in all_books:
    print(book)
