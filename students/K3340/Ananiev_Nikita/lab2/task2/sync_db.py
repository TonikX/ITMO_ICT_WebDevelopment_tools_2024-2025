import dotenv
import psycopg2
import os
from copy import copy
from datetime import datetime
import requests
import queue
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

dotenv.load_dotenv()

def retrieve_book_fields(book):
    allowed_fields = {"title", "author", "release_date", "subject"}
    all_keys = copy(list(book.keys()))
    for k in all_keys:
        if not k in allowed_fields:
            del book[k]
    book["genre"] = book["subject"]
    del book["subject"]
    book["release_date"] = datetime.strptime(book['release_date'], '%b %d, %Y').date()


class SyncDBFiller:
    def __init__(self, lock=None):
        self.conn = psycopg2.connect(os.getenv("DB_CONN"))
        self.lock = lock

    def disconnect(self):
        self.conn.close()

    def add_book(self, book, source):
        retrieve_book_fields(book)
        book["publisher"] = source
        err = None
        try:
            if self.lock:
                self.lock.acquire()
            with self.conn.cursor() as cursor:
                cursor.execute(
            'INSERT INTO bookinfo (author, title, release_date, genre, publisher) VALUES (%s, %s, %s, %s, %s)',
             (book["author"], book["title"], book["release_date"], book["genre"], book["publisher"])
                )
                self.conn.commit()
        except BaseException as e:
            self.conn.rollback()
            err = e
        finally:
            if self.lock:
                self.lock.release()
        return err


class SessionPool:
    def __init__(self, size=10):
        self.queue = queue.Queue(maxsize=size)
        for _ in range(size):
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504]
            )
            session = requests.Session()
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            self.queue.put(session)

    def get_session(self):
        return self.queue.get()

    def put_session(self, session):
        self.queue.put(session)
