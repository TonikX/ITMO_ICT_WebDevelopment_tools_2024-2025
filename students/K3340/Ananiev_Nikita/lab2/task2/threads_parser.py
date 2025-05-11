import time
from threading import Thread, Lock
from helpers import SessionPool, tpl, base, parse_book_links, parse_book_details

from database import SyncDBFiller

threads_count = 4
books_count = 100
books_saved = 0
a = 0
filler = SyncDBFiller(Lock())
lock = Lock()
session_pool = SessionPool(size=threads_count)

def get_book_links(pool, pages):
    links = []
    s = pool.get_session()
    for page in pages:
        resp = s.get(page)
        links.extend(parse_book_links(resp.content))
    pool.put_session(s)
    return links

def parse_and_save(links):
    global books_saved, a
    s = session_pool.get_session()
    for link in links:
        resp = s.get(link)
        details = parse_book_details(resp.content)
        err = filler.add_book(details, "from threads")
        if err is None:
            with lock:
                books_saved += 1

def main():
    start_index = 100
    pages = [base + tpl.format(index) for index in range(start_index + 1, start_index + books_count + 1, 25)]
    all_links = get_book_links(session_pool, pages)
    per_thread = books_count // threads_count
    threads = [
        Thread(target=parse_and_save, args=(all_links[i:i + per_thread],)) for i in range(0, books_count, per_thread)
    ]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    start = time.time()
    main()
    print("TIME PASSED:", time.time() - start)
    print("BOOKS SAVED:", books_saved)
    filler.disconnect()
