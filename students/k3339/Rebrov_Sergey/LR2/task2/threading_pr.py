import time
import requests
import threading
from bs4 import BeautifulSoup

from config import *
from models import *
from connection import *


def parse_and_save(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title else "No title"

    with get_session() as session:
        page = Page(url=url, title=title)
        session.merge(page)
        session.commit()


def main():
    init_db()

    start = time.time()

    threads = []
    for url in URLS:
        t = threading.Thread(target=parse_and_save, args=(url,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print(f"Время: {time.time() - start:.2f} сек")


if __name__ == "__main__":
    main()
