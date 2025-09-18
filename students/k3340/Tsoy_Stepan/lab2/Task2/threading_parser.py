import time
import threading
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
    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.title.string.strip() if soup.title else "No title"
    save_title_to_db(title)
    print(f"[threading] {url} -> {title}")

def main():
    start = time.perf_counter()
    threads = []
    for url in URLS:
        t = threading.Thread(target=parse_and_save, args=(url,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    print(f"[threading] Finished in {time.perf_counter() - start:.2f}s")

if __name__ == "__main__":
    main()
