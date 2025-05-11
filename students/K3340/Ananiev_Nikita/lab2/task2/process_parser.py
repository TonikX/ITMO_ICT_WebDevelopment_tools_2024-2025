import time
import multiprocessing
from database import SyncDBFiller
from helpers import SessionPool, base, tpl, parse_book_details
from threads_parser import get_book_links

process_count = 4
books_count = 100
books_saved = 0

def parse_and_save(args):
    saved = 0
    db = SyncDBFiller()
    session, links = args[0], args[1]
    for link in links:
        resp = session.get(link)
        details = parse_book_details(resp.content)
        err = db.add_book(details, source="from process")
        if err is None:
            saved += 1
    db.disconnect()
    return saved


def main():
    global books_count, books_saved
    start_index = 200
    session_pool = SessionPool(size=process_count)
    pages = [base + tpl.format(index) for index in range(start_index + 1, start_index + books_count + 1, 25)]
    all_links = get_book_links(session_pool, pages)
    per_process = books_count // process_count
    links_per_process = [all_links[i:i + per_process] for i in range(0, books_count, per_process)]
    args = [
        (
            session_pool.get_session(),
            links_per_process[i],
        )
        for i in range(process_count)
    ]
    print(len(args))
    with multiprocessing.Pool(processes=process_count) as pool:
        book_saved_it = pool.imap(parse_and_save, args)
        books_saved = sum(book_saved_it)


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("TIME PASSED:", time.time() - start_time)
    print("BOOKS SAVED:", books_saved)
