import asyncio
import time
from urllib.parse import urljoin
import aiohttp
from bs4 import BeautifulSoup


async def get_all_books(session):
    book_urls = []
    current_url = URL

    while True:
        async with session.get(current_url) as response:
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')

            book_links = soup.select('h3 a')
            for link in book_links:
                book_url = urljoin(current_url, link['href'])
                book_urls.append(book_url)

            next_button = soup.select_one('li.next a')
            if not next_button:
                break
            current_url = urljoin(current_url, next_button['href'])

    return book_urls


async def parse_and_save(session, book_url):
    try:
        async with session.get(book_url) as response:
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')
            title = soup.find("div", class_="product_main").h1.string
            description_tag = soup.find("div", id="product_description")
            description = description_tag.find_next_sibling("p").string if description_tag else None

            async with session.post(
                    "http://127.0.0.1:8000/books/",
                    json={
                        "title": title,
                        "description": description
                    },
                    headers={"Content-Type": "application/json"}
            ) as api_response:
                if api_response.status == 201:
                    return True, title
                return False, title

    except Exception as e:
        print(f"Error processing {book_url}: {e}")
        return False, None


async def worker(session, book_urls, results, worker_id):
    for url in book_urls:
        success, title = await parse_and_save(session, url)
        if success:
            results.append(title)
            print(f"Worker {worker_id}: Saved {title}")
        else:
            print(f"Worker {worker_id}: Failed to save {url}")


async def main(count_of_workers):
    start_time = time.time()
    connector = aiohttp.TCPConnector(limit_per_host=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        book_urls = await get_all_books(session)
        size = len(book_urls) // count_of_workers
        results = []
        tasks = []
        for i in range(count_of_workers):
            start_idx = i * size
            end_idx = start_idx + size if i < count_of_workers - 1 else len(book_urls)
            worker_urls = book_urls[start_idx:end_idx]

            task = asyncio.create_task(worker(session, worker_urls, results, i + 1))
            tasks.append(task)
        await asyncio.gather(*tasks)
        print(f"\nSaved {len(results)}/{len(book_urls)} books")
        end_time = time.time()
        print(f"Time: {end_time - start_time:.2f} seconds")


if __name__ == '__main__':
    URL = 'https://books.toscrape.com/catalogue/category/books/nonfiction_13/index.html'
    asyncio.run(main(10))
