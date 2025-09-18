import time
import multiprocessing
import requests
from bs4 import BeautifulSoup
from db_utils import save_title_to_db

URLS = [
    "https://store.steampowered.com/",
    "https://www.nalog.gov.ru/",
    "https://worldoftanks.eu/",
    "https://itmo.ru/",
    "https://www.aviasales.ru/",
]

def parse_and_save(url: str):
    resp = requests.get(url, timeout=10)
    from bs4 import BeautifulSoup  # safe import in child
    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.title.string.strip() if soup.title else "No title"
    save_title_to_db(title)
    print(f"[multiprocessing] {url} -> {title}")

def main():
    start = time.perf_counter()
    with multiprocessing.Pool(processes=5) as pool:
        pool.map(parse_and_save, URLS)
    print(f"[multiprocessing] Finished in {time.perf_counter() - start:.2f}s")

if __name__ == "__main__":
    main()
