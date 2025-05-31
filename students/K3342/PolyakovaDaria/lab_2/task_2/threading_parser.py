import threading
import time
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session
from db import engine, init_db
from models import ParsedPage
from urls import urls


def parse_and_save(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        title = soup.title.string if soup.title else "No title"
        with Session(engine) as session:
            page = ParsedPage(url=url, title=title)
            session.add(page)
            session.commit()
        print(f"[Threading] Parsed: {url} — {title}")
    except Exception as e:
        print(f"Error: {url} — {e}")


def main():
    init_db()
    threads = []
    start = time.time()
    for url in urls:
        t = threading.Thread(target=parse_and_save, args=(url,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    print("Threading Done in", time.time() - start, "seconds")


if __name__ == "__main__":
    main()
