import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
from models import BookCreate

fastapi_base = "http://lab_1:8000/"


async def parse_and_save(catalog_url: str):
    queue: asyncio.Queue[BookCreate] = asyncio.Queue()

    start = time.time()
    async with (
        aiohttp.ClientSession() as site_session,
        aiohttp.ClientSession() as fastapi_session,
    ):
        print(f"[MAIN] Fetching catalog page: {catalog_url}")
        async with site_session.get(catalog_url) as response:
            response.raise_for_status()
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

        book_cards = soup.find_all("article")
        book_links = [urljoin(catalog_url, card.h3.a["href"]) for card in book_cards]
        print(f"[MAIN] Found {len(book_links)} books.")

        producer_tasks = [parse_book(queue, site_session, link) for link in book_links]
        consumer_tasks = [
            asyncio.create_task(consumer(queue, fastapi_session, i)) for i in range(5)
        ]

        await asyncio.gather(*producer_tasks)
        # print("[MAIN] All books parsed and put into queue.")
        await queue.join()

        # print("[MAIN] All tasks completed. Cancelling consumers...")
        for task in consumer_tasks:
            task.cancel()

        await asyncio.gather(*consumer_tasks, return_exceptions=True)
        print("[MAIN] Done in", time.time() - start, "seconds")
    return {
        "url": catalog_url,
        "parsed_count": len(book_links),
        "duration": time.time() - start,
    }


async def parse_book(
    queue: asyncio.Queue, session: aiohttp.ClientSession, book_url: str
) -> BookCreate | None:
    try:
        # print(f"[PARSE_BOOK] Start parsing: {book_url}")
        async with session.get(book_url) as response:
            response.raise_for_status()
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
        title = soup.find("div", class_="product_main").h1.string
        desc = soup.find("div", id="product_description").find_next_sibling("p").string
        new_book = BookCreate.model_validate({"title": title, "description": desc})
        await queue.put(new_book)
        print(f"[PARSE_BOOK] Parsed and added to queue: {title}")

    except Exception as e:
        print(f"Error parsing {book_url}: {e}")
        return None


async def save(fastapi_session, book: BookCreate):
    # print(f"[SAVE] Saving book to DB: {book.title}")

    try:
        endpoint = fastapi_base + "books/"
        async with fastapi_session.post(endpoint, json=book.model_dump()) as resp:
            resp.raise_for_status()
            print(f"[SAVE] {resp.status} Saved book: {book.title}")
    except Exception as e:
        print(f"[SAVE] Error saving {book.title}: {e}")


async def consumer(queue: asyncio.Queue, fastapi_session, consumer_id: int):
    # print(f"[CONSUMER {consumer_id}] Started.")
    while True:
        book_to_save = await queue.get()
        if book_to_save:
            # print(f"[CONSUMER {consumer_id}] Got book: {book_to_save.title}")
            await save(fastapi_session, book_to_save)
        queue.task_done()
