import asyncio
import aiohttp
import random
import time
from bs4 import BeautifulSoup
from sqlmodel import Session
from connection import db
from models.models import Book
from base import clean_description

GENRE_URLS = {
    "Science Fiction": "https://www.goodreads.com/shelf/show/science-fiction",
    "Mystery": "https://www.goodreads.com/shelf/show/mystery",
    "Historical Fiction": "https://www.goodreads.com/shelf/show/historical-fiction",
    "Romance": "https://www.goodreads.com/shelf/show/romance",
    "Young Adult": "https://www.goodreads.com/shelf/show/young-adult"
}

HEADERS_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (X11; Linux x86_64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
]

async def fetch_html(session: aiohttp.ClientSession, url: str) -> str:
    headers = {
        "User-Agent": random.choice(HEADERS_LIST),
        "Accept": "...",
        "Accept-Language": "...",
        "Referer": "..."
    }
    async with session.get(url, headers=headers, timeout=10) as response:
        return await response.text()

async def parse_books(session, genre_url, genre_name, max_books=3):
    books = []
    try:
        html_content = await fetch_html(session, genre_url)
        await asyncio.sleep(random.uniform(1.5, 3.0))
        soup = BeautifulSoup(html_content, "html.parser")
        book_items = soup.select("div.elementList")[:max_books]

        for item in book_items:
            try:
                title_tag = item.find("a", class_="bookTitle")
                author_tag = item.find("a", class_="authorName")
                if not title_tag or not author_tag:
                    continue

                title = title_tag.text.strip()
                author = author_tag.text.strip()

                # Goodreads shelf pages may not provide ISBN, publisher, or publication year directly.
                # These details would require accessing individual book pages, which is more complex.
                isbn = None
                published_in = None
                publisher = None

                description = None  # Not available on shelf pages

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
                print(f"Error parsing book: {e}")
                continue
    except Exception as e:
        print(f"Error fetching HTML for genre {genre_name}: {e}")

    return books

def save_books_to_db(books):
    with Session(engine) as session:
        for book_data in books:
            book = Book(**book_data)
            session.add(book)
        session.commit()

async def process_genre(session, genre_name, genre_url):
    books = await parse_books(session, genre_url, genre_name)
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, save_books_to_db, books)
    print(f"[{genre_name}] Saved {len(books)} books")

async def main():
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [process_genre(session, genre, url) for genre, url in GENRE_URLS.items()]
        await asyncio.gather(*tasks)
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
