from multiprocessing import Pool
import time
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session
from connection import engine
from models import Page
from lr2.task2.urls import urls

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
    start = time.time()
    with Pool(4) as pool:
        pool.map(parse_and_save, urls)

    end = time.time()
    print(f"\nMultiprocessing time: {end - start:.2f} seconds")

if __name__ == "__main__":
    main()