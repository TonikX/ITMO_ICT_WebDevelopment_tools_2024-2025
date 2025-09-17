from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session
from db import engine, init_db
from models import Book, Genres

BASE_URL = "https://books.toscrape.com/catalogue/category/books_1/index.html"

def fetch_books_sync():
    r = requests.get(BASE_URL)
    soup = BeautifulSoup(r.text, "html.parser")
    books = []
    for book_tag in soup.select(".product_pod"):
        title = book_tag.select_one("h3 a")["title"]
        author_tag = book_tag.select_one(".author")
        author = author_tag.text.strip() if author_tag else "Unknown"
        genre_enum = Genres.non_fi
        published_year = 2025
        books.append(Book(title=title, author=author, genre=genre_enum, published_year=published_year))
    return books

def save_books(books):
    if not books:
        return
    with Session(engine) as session:
        for book in books:
            session.add(book)
        session.commit()

def run_threading():
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_books_sync) for _ in range(5)]
        all_books = []
        for f in futures:
            all_books.extend(f.result())
        save_books(all_books)
        print(f"Добавлено книг (threading): {len(all_books)}")

if __name__ == "__main__":
    init_db()
    run_threading()
