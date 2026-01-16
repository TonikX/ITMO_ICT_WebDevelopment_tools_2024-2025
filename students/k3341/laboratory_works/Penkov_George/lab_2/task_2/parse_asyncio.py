import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time
from lab_1.models.books import BookCreate


async def parse_book(
    queue: asyncio.Queue, session: aiohttp.ClientSession, url: str
) -> BookCreate | None:
    try:
        print(f"[PARSE_BOOK] Start parsing: {url}")
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            title = soup.find("div", class_="product_main").h1.string
            desc = (
                soup.find("div", id="product_description").find_next_sibling("p").string
            )
            new_book = BookCreate.model_validate({"title": title, "description": desc})
            await queue.put(new_book)
            print(f"[PARSE_BOOK] Parsed and added to queue: {title}")
    except Exception as e:
        print(f"Error parsing {url}: {e}")
        return None


async def save(fastapi_session, book: BookCreate):
    print(f"[SAVE] Saving book to DB: {book.title}")
    try:
        async with fastapi_session.post("books/", json=book.model_dump()) as resp:
            print(f"[SAVE] {resp.status} Saved book: {book.title}")
    except Exception as e:
        print(f"[SAVE] Error saving {book.title}: {e}")


async def consumer(queue: asyncio.Queue, fastapi_session, consumer_id: int):
    print(f"[CONSUMER {consumer_id}] Started.")
    while True:
        book_to_save = await queue.get()
        if book_to_save:
            print(f"[CONSUMER {consumer_id}] Got book: {book_to_save.title}")
            await save(fastapi_session, book_to_save)
        queue.task_done()


async def main():
    queue = asyncio.Queue()

    start = time.time()
    async with (
        aiohttp.ClientSession(base_url="https://books.toscrape.com/") as site_session,
        aiohttp.ClientSession(base_url="http://localhost:8000/") as fastapi_session,
    ):
        print("[MAIN] Fetching main page...")
        async with site_session.get("index.html") as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            book_cards = soup.find_all("article")
            book_links = [card.h3.a["href"] for card in book_cards]

        print(f"[MAIN] Found {len(book_links)} books.")
        producer_tasks = [parse_book(queue, site_session, link) for link in book_links]

        consumer_tasks = [
            asyncio.create_task(consumer(queue, fastapi_session, i)) for i in range(10)
        ]

        await asyncio.gather(*producer_tasks)
        print("[MAIN] All books parsed and put into queue.")
        await queue.join()

        print("[MAIN] All tasks completed. Cancelling consumers...")
        for task in consumer_tasks:
            task.cancel()

        await asyncio.gather(*consumer_tasks, return_exceptions=True)
        print("[MAIN] Done in", time.time() - start, "seconds")


if __name__ == "__main__":
    asyncio.run(main())


"""

[MAIN] Fetching main page...
[MAIN] Found 20 books.
[CONSUMER 0] Started.
[CONSUMER 1] Started.
[CONSUMER 2] Started.
[CONSUMER 3] Started.
[CONSUMER 4] Started.
[CONSUMER 5] Started.
[CONSUMER 6] Started.
[CONSUMER 7] Started.
[CONSUMER 8] Started.
[CONSUMER 9] Started.
[PARSE_BOOK] Start parsing: catalogue/a-light-in-the-attic_1000/index.html
[PARSE_BOOK] Start parsing: catalogue/tipping-the-velvet_999/index.html
[PARSE_BOOK] Start parsing: catalogue/soumission_998/index.html
[PARSE_BOOK] Start parsing: catalogue/sharp-objects_997/index.html
[PARSE_BOOK] Start parsing: catalogue/sapiens-a-brief-history-of-humankind_996/index.html
[PARSE_BOOK] Start parsing: catalogue/the-requiem-red_995/index.html
[PARSE_BOOK] Start parsing: catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html       
[PARSE_BOOK] Start parsing: catalogue/the-coming-woman-a-novel-based-on-the-life-of-the-infamous-feminist-victoria-woodhull_993/index.html
[PARSE_BOOK] Start parsing: catalogue/the-boys-in-the-boat-nine-americans-and-their-epic-quest-for-gold-at-the-1936-berlin-olympics_992/index.html
[PARSE_BOOK] Start parsing: catalogue/the-black-maria_991/index.html
[PARSE_BOOK] Start parsing: catalogue/starving-hearts-triangular-trade-trilogy-1_990/index.html
[PARSE_BOOK] Start parsing: catalogue/shakespeares-sonnets_989/index.html
[PARSE_BOOK] Start parsing: catalogue/set-me-free_988/index.html
[PARSE_BOOK] Start parsing: catalogue/scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html      
[PARSE_BOOK] Start parsing: catalogue/rip-it-up-and-start-again_986/index.html
[PARSE_BOOK] Start parsing: catalogue/our-band-could-be-your-life-scenes-from-the-american-indie-underground-1981-1991_985/index.html
[PARSE_BOOK] Start parsing: catalogue/olio_984/index.html
[PARSE_BOOK] Start parsing: catalogue/mesaerion-the-best-science-fiction-stories-1800-1849_983/index.html     
[PARSE_BOOK] Start parsing: catalogue/libertarianism-for-beginners_982/index.html
[PARSE_BOOK] Start parsing: catalogue/its-only-the-himalayas_981/index.html
[PARSE_BOOK] Parsed and added to queue: A Light in the Attic
[CONSUMER 0] Got book: A Light in the Attic
[SAVE] Saving book to DB: A Light in the Attic
[SAVE] 200 Saved book: A Light in the Attic
[PARSE_BOOK] Parsed and added to queue: The Dirty Little Secrets of Getting Your Dream Job
[CONSUMER 1] Got book: The Dirty Little Secrets of Getting Your Dream Job
[SAVE] Saving book to DB: The Dirty Little Secrets of Getting Your Dream Job
[PARSE_BOOK] Parsed and added to queue: The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull
[PARSE_BOOK] Parsed and added to queue: Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)
[CONSUMER 2] Got book: The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull
[SAVE] Saving book to DB: The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull
[CONSUMER 3] Got book: Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)
[SAVE] Saving book to DB: Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)
[PARSE_BOOK] Parsed and added to queue: Sapiens: A Brief History of Humankind
[PARSE_BOOK] Parsed and added to queue: Shakespeare's Sonnets
[PARSE_BOOK] Parsed and added to queue: Tipping the Velvet
[PARSE_BOOK] Parsed and added to queue: Libertarianism for Beginners
[PARSE_BOOK] Parsed and added to queue: The Black Maria
[PARSE_BOOK] Parsed and added to queue: Starving Hearts (Triangular Trade Trilogy, #1)
[PARSE_BOOK] Parsed and added to queue: Olio
[PARSE_BOOK] Parsed and added to queue: Soumission
[PARSE_BOOK] Parsed and added to queue: It's Only the Himalayas
[SAVE] 200 Saved book: The Dirty Little Secrets of Getting Your Dream Job
[CONSUMER 1] Got book: Sapiens: A Brief History of Humankind
[SAVE] Saving book to DB: Sapiens: A Brief History of Humankind
[CONSUMER 4] Got book: Shakespeare's Sonnets
[SAVE] Saving book to DB: Shakespeare's Sonnets
[CONSUMER 5] Got book: Tipping the Velvet
[SAVE] Saving book to DB: Tipping the Velvet
[CONSUMER 6] Got book: Libertarianism for Beginners
[SAVE] Saving book to DB: Libertarianism for Beginners
[CONSUMER 7] Got book: The Black Maria
[SAVE] Saving book to DB: The Black Maria
[CONSUMER 8] Got book: Starving Hearts (Triangular Trade Trilogy, #1)
[SAVE] Saving book to DB: Starving Hearts (Triangular Trade Trilogy, #1)
[CONSUMER 9] Got book: Olio
[SAVE] Saving book to DB: Olio
[CONSUMER 0] Got book: Soumission
[SAVE] Saving book to DB: Soumission
[PARSE_BOOK] Parsed and added to queue: The Requiem Red
[PARSE_BOOK] Parsed and added to queue: Mesaerion: The Best Science Fiction Stories 1800-1849
[PARSE_BOOK] Parsed and added to queue: Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991
[PARSE_BOOK] Parsed and added to queue: Sharp Objects
[PARSE_BOOK] Parsed and added to queue: Set Me Free
[PARSE_BOOK] Parsed and added to queue: The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics
[PARSE_BOOK] Parsed and added to queue: Rip it Up and Start Again
[MAIN] All books parsed and put into queue.
[SAVE] 200 Saved book: Sapiens: A Brief History of Humankind
[CONSUMER 1] Got book: It's Only the Himalayas
[SAVE] Saving book to DB: It's Only the Himalayas
[SAVE] 200 Saved book: It's Only the Himalayas
[CONSUMER 1] Got book: The Requiem Red
[SAVE] Saving book to DB: The Requiem Red
[SAVE] 200 Saved book: Soumission
[CONSUMER 0] Got book: Mesaerion: The Best Science Fiction Stories 1800-1849
[SAVE] Saving book to DB: Mesaerion: The Best Science Fiction Stories 1800-1849
[SAVE] 200 Saved book: Shakespeare's Sonnets
[CONSUMER 4] Got book: Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991     
[SAVE] Saving book to DB: Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991  
[SAVE] 200 Saved book: The Coming Woman: A Novel Based on the Life of the Infamous Feminist, Victoria Woodhull
[CONSUMER 2] Got book: Sharp Objects
[SAVE] Saving book to DB: Sharp Objects
[SAVE] 200 Saved book: Libertarianism for Beginners
[CONSUMER 6] Got book: Set Me Free
[SAVE] Saving book to DB: Set Me Free
[SAVE] 200 Saved book: Mesaerion: The Best Science Fiction Stories 1800-1849
[CONSUMER 0] Got book: The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics
[SAVE] Saving book to DB: The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics
[SAVE] 200 Saved book: Our Band Could Be Your Life: Scenes from the American Indie Underground, 1981-1991     
[CONSUMER 4] Got book: Rip it Up and Start Again
[SAVE] Saving book to DB: Rip it Up and Start Again
[SAVE] 200 Saved book: Sharp Objects
[SAVE] 200 Saved book: Set Me Free
[SAVE] 200 Saved book: Starving Hearts (Triangular Trade Trilogy, #1)
[SAVE] 200 Saved book: Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)
[SAVE] 200 Saved book: The Boys in the Boat: Nine Americans and Their Epic Quest for Gold at the 1936 Berlin Olympics
[SAVE] 200 Saved book: Olio
[SAVE] 200 Saved book: The Black Maria
[SAVE] 200 Saved book: Tipping the Velvet
[SAVE] 200 Saved book: The Requiem Red
[SAVE] 200 Saved book: Rip it Up and Start Again
[MAIN] All tasks completed. Cancelling consumers...
[MAIN] Done in 2.245100975036621 seconds

"""
