from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import random
import time
import logging
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("__main__")

urls = {
    "Современная зарубежная литература": "https://www.livelib.ru/genre/Современная-зарубежная-литература",
    "Зарубежная классика": "https://www.livelib.ru/genre/Зарубежная-классика",
    "Зарубежные детективы": "https://www.livelib.ru/genre/Зарубежные-детективы",
    "Фэнтези": "https://www.livelib.ru/genre/Фэнтези",
    "Приключения": "https://www.livelib.ru/genre/Приключения",
    "Эзотерика": "https://www.livelib.ru/genre/Эзотерика",
    "Фантастика": "https://www.livelib.ru/genre/Фантастика",
    "Книги по психологии": "https://www.livelib.ru/genre/Книги по психологии",
    "Любовные романы": "https://www.livelib.ru/genre/Любовные романы"
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0"
]

def clean_description(text: str) -> str:
    text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    cutoff_phrases = ["Развернуть", "развернуть"]
    for phrase in cutoff_phrases:
        if phrase in text:
            return text.split(phrase)[0].strip() + "..."
    return text.strip()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: logger.debug(
        f"Retrying ({retry_state.attempt_number}/3) after {retry_state.idle_for}s due to {retry_state.outcome.exception()}"
    )
)
async def load_page(page, url):
    logger.debug(f"Attempting to load page: {url}")
    await page.goto(url, timeout=120000)
    await page.wait_for_load_state("networkidle", timeout=60000)
    logger.debug("Page load completed")
    return page

async def parse_books_from_genre_page(url, genre_name, max_books=3):
    books = []
    logger.debug(f"Parsing URL: {url}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_extra_http_headers({
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br"
            })

            time.sleep(random.uniform(3.0, 6.0))
            logger.debug("Navigating to page")
            await load_page(page, url)
            logger.debug(f"Initial page loaded: {page.url}")
            logger.debug(f"Initial page content: {(await page.content())[:1000]}")

            if "ratelimitcaptcha" in page.url:
                logger.debug("Rate-limit page detected, waiting for redirect")
                await page.wait_for_timeout(20000)
                await page.wait_for_load_state("networkidle", timeout=60000)
                logger.debug(f"After wait, current URL: {page.url}")
                logger.debug(f"After wait, page content: {(await page.content())[:1000]}")

            if not ("genre" in page.url or "tag" in page.url):
                logger.error(f"Failed to reach genre or tag page, final URL: {page.url}")
                await browser.close()
                return books

            soup = BeautifulSoup(await page.content(), "html.parser")
            book_items = soup.select("li.book-item__item")[:max_books]
            logger.debug(f"Found {len(book_items)} book items")

            for item in book_items:
                try:
                    title_tag = item.find("a", class_="book-item__title")
                    author_tag = item.find("a", class_="book-item__author")
                    if not title_tag or not author_tag:
                        logger.warning("Missing title or author tag in book item")
                        continue

                    title = title_tag.text.strip()
                    author = author_tag.text.strip()
                    logger.debug(f"Parsing book: {title} by {author}")

                    info_table = item.find("table", class_="book-item-edition")
                    isbn, publication_year, publisher = None, None, None
                    if info_table:
                        rows = info_table.find_all("tr")
                        for row in rows:
                            cells = row.find_all("td")
                            if len(cells) < 2:
                                continue
                            label = cells[0].text.strip()
                            value = cells[1].text.strip()
                            if label == "ISBN:":
                                isbn = value
                            elif label == "Год издания:":
                                publication_year = int(value) if value.isdigit() else None
                            elif label == "Издательство:":
                                publisher = value

                    publisher = publisher.replace('\xa0', ' ').replace('\r', '').replace('\n', '').strip() if publisher else None
                    publisher = ', '.join(part.strip() for part in publisher.split(',')) if publisher else None

                    description_div = item.find("div", class_="book-item__text")
                    description = description_div.get_text(separator="\n").strip() if description_div else None
                    description = clean_description(description) if description else None

                    book_data = {
                        "title": title,
                        "author": author,
                        "genre": genre_name,
                        "isbn": isbn,
                        "publication_year": publication_year,
                        "condition": "unknown",
                        "description": description
                    }
                    logger.debug(f"Parsed book data: {book_data}")
                    books.append(book_data)
                except Exception as e:
                    logger.error(f"Error parsing book item: {e}")
                    continue

            await browser.close()
    except Exception as e:
        logger.error(f"Error fetching or parsing HTML: {e}")

    logger.debug(f"Total books parsed: {len(books)}")
    return books