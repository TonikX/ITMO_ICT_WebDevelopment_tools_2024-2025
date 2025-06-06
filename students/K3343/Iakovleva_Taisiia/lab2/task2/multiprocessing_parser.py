from multiprocessing import Pool
import requests, time
from bs4 import BeautifulSoup
from models import ParsedPage
from db import engine
from sqlmodel import Session
from urls import URLS

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}


def parse_and_save(url):
    try:
        html = requests.get(url, headers=headers, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title else "No title"
    except Exception as e:
        title = f"[ERROR] {e}"
    with Session(engine) as db:
        db.add(ParsedPage(url=url, title=title))
        db.commit()
    print(f"[{url}] -> {title}")

if __name__ == "__main__":
    start = time.perf_counter()
    with Pool() as pool:
        pool.map(parse_and_save, URLS)
    print(f"Finished in {time.perf_counter() - start:.2f}s")
