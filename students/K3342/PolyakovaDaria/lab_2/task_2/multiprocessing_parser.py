import time
import requests
from bs4 import BeautifulSoup
from multiprocessing import Process
from sqlmodel import Session
from models import ParsedPage
from db import engine
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
        print(f"[Multiprocessing] Parsed: {url} — {title}")
    except Exception as e:
        print(f"Error: {url} — {e}")


def main():
    from db import init_db
    init_db()
    processes = []
    start = time.time()
    for url in urls:
        p = Process(target=parse_and_save, args=(url,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
    print("Multiprocessing Done in", time.time() - start, "seconds")


if __name__ == "__main__":
    main()
