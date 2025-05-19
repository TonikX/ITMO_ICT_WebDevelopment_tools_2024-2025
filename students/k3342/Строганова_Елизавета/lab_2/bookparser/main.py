import asyncio
from bookparser.parser_async import parse_book_list
from bookparser.db_save import save_books
from bookparser.config import CATEGORY_URLS

async def process_genre(session, genre, url):
    books = await parse_book_list(session, url, genre)
    save_books(books)
    print(f"[{genre}] Сохранено {len(books)} книг")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [process_genre(session, genre, url) for genre, url in CATEGORY_URLS.items()]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
