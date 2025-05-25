import time
from multiprocessing import Pool, cpu_count
import requests
from parser import tpl, base, parse_book_links, parse_book_details
from db import SyncDBFiller

WORKERS = min(cpu_count(), 4)
BOOKS_TOTAL = 100

def init_links():
    pages = [base + tpl.format(i) for i in range(1, BOOKS_TOTAL+1, 25)]
    links = []
    for url in pages:
        try:
            r = requests.get(url, timeout=10)
            links.extend(parse_book_links(r.content))
        except Exception:
            continue
    return links

def parse_and_save(chunk: list[str]) -> int:
    filler = SyncDBFiller()
    saved = 0
    session = requests.Session()
    for url in chunk:
        try:
            r = session.get(url, timeout=10)
            details = parse_book_details(r.content)
            if filler.add_book(details, "process"):
                saved += 1
        except Exception:
            continue
    filler.disconnect()
    return saved

def main():
    all_links = init_links()
    per = (len(all_links) + WORKERS - 1) // WORKERS
    chunks = [all_links[i:i+per] for i in range(0, len(all_links), per)]

    t0 = time.time()
    with Pool(WORKERS) as pool:
        results = pool.map(parse_and_save, chunks)
    total = sum(results)
    print(f"[multiprocessing] saved {total} books in {time.time()-t0:.2f}s")

if __name__ == "__main__":
    main()