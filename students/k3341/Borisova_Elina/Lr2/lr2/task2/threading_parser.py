import threading
import time
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session, SQLModel
from connection import engine
from lr2.task2.urls import urls
from models import Page

def parse_and_save(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        bs = BeautifulSoup(response.text, "html.parser")
        title = bs.title.string if bs.title else None

        with Session(engine) as db:
            page = Page(url=url, title=title)
            db.add(page)
            db.commit()
            print(f"Parsed: {url} | Title: {title}")
    except Exception as e:
        print(f"Error parsing {url}: {e}")

def main():
    threads = []

    start = time.time()
    for url in urls:
        thread = threading.Thread(target=parse_and_save, args=(url,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end = time.time()
    print(f"\nThreading time: {end - start:.2f} seconds")

if __name__ == "__main__":
    main()