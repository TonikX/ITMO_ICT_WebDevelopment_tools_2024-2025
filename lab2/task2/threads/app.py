import os
import sys
import threading
import time
import requests
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import create_book_record
from urls import MAX_PAGES, url


def parse_and_save(url: str):
    try:
        print(f"Fetching {url}...")
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        book_items = soup.find_all("li", class_="book-item__item book-item--full")
        for book in book_items:
            title = book.find("a", class_="book-item__title")
            author = book.find("a", class_="book-item__author")
            isbn = book.find("table", class_="book-item-edition")
            description = book.find("div", id="lenta-card__text-edition-full")
            if description is None:
                description = book.find("div", id="lenta-card__text-edition-escaped")
            title_text = title.get_text(strip=True) if title else None
            author_text = author.get_text(strip=True) if author else None
            isbn_text = None
            if isbn:
                td = isbn.find("td", class_=None)
                isbn_text = td.get_text(strip=True) if td else None
            description_text = description.get_text(strip=True) if description else None
            create_book_record(title_text, author_text, isbn_text, description_text)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
    except Exception as e:
        print(f"Error parsing {url}: {e}")


def worker(url: str, result_list: list, index: int):
    result_list[index] = parse_and_save(url)


if __name__ == "__main__":
    results = [None] * MAX_PAGES
    threads = []

    t0 = time.perf_counter()
    for i in range(1, MAX_PAGES + 1):
        page_url = url.format(page=i)
        th = threading.Thread(target=worker, args=(page_url, results, i - 1))
        th.start()
        threads.append(th)

    for th in threads:
        th.join()
    t1 = time.perf_counter()

    print(f"Threading: time = {t1 - t0:.2f} s")
