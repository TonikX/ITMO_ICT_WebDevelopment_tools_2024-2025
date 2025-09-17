import aiohttp
import asyncio
from bs4 import BeautifulSoup
from db import AsyncSessionLocal, async_init_db
from models import Book, Genres

BASE_URL = "https://books.toscrape.com/catalogue/category/books_1/index.html"

async def fetch_books_async():
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL) as response:
            text = await response.text()
            soup = BeautifulSoup(text, "html.parser")
            books = []
            for book_tag in soup.select(".product_pod"):
                title = book_tag.select_one("h3 a")["title"]
                author_tag = book_tag.select_one(".author")
                author = author_tag.text.strip() if author_tag else "Unknown"
                genre_enum = Genres.non_fi
                published_year = 2025
                books.append(Book(
                    title=title,
                    author=author,
                    genre=genre_enum,
                    published_year=published_year
                ))
            return books

async def save_books_async(books):
    if not books:
        return
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for book in books:
                session.add(book)

async def run_async():
    books = await fetch_books_async()
    await save_books_async(books)
    print(f"Добавлено книг: {len(books)}")

async def main():
    await async_init_db()
    await run_async()

if __name__ == "__main__":
    asyncio.run(main())
