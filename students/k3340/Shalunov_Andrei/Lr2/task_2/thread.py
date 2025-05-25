import time
from threading import Thread, Lock
from parser import SessionPool, tpl, base, parse_book_links, parse_book_details
from db import SyncDBFiller

THREADS = 4
BOOKS_TOTAL = 100

def get_book_links(pool: SessionPool, pages: list[str]) -> list[str]:
    session = pool.get_session()
    links: list[str] = []
    for url in pages:
        try:
            resp = session.get(url, timeout=10)
            html = resp.content
            links.extend(parse_book_links(html))
        except Exception as e:
            print(f"[get_links] error {url}: {e}")
    pool.put_session(session)
    return links

def worker(links: list[str], pool: SessionPool, filler: SyncDBFiller, lock: Lock) -> int:
    saved = 0
    session = pool.get_session()
    for url in links:
        try:
            resp = session.get(url, timeout=10)
            details = parse_book_details(resp.content)
            if filler.add_book(details, "thread"):
                saved += 1
        except Exception as e:
            print(f"[thread worker] error {url}: {e}")
    pool.put_session(session)
    return saved

def main():
    pool = SessionPool(size=THREADS)
    filler = SyncDBFiller(lock=Lock())
    pages = [base + tpl.format(i) for i in range(1, BOOKS_TOTAL+1, 25)]
    all_links = get_book_links(pool, pages)

    per_thread = (len(all_links) + THREADS - 1) // THREADS
    threads: list[Thread] = []
    results: list[int] = []
    results_lock = Lock()

    def run_slice(slice_):
        cnt = worker(slice_, pool, filler, filler.lock)
        with results_lock:
            results.append(cnt)

    t0 = time.time()
    for i in range(0, len(all_links), per_thread):
        slice_ = all_links[i:i+per_thread]
        t = Thread(target=run_slice, args=(slice_,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    filler.disconnect()

    total_saved = sum(results)
    print(f"[threading] saved {total_saved} books in {time.time()-t0:.2f}s")

if __name__ == "__main__":
    main()