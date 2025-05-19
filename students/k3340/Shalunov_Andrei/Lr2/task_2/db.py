import dotenv
import asyncpg
import psycopg2
import os
from copy import copy
from datetime import datetime

dotenv.load_dotenv()

def retrieve_book_fields(book: dict):
    allowed = {"title", "author", "release_date", "subject"}
    for k in list(book.keys()):
        if k not in allowed:
            del book[k]

    genre = book.get("subject", "")
    book["genre"] = genre
    book.pop("subject", None)

    date_str = book.get("release_date")
    if date_str:
        book["release_date"] = datetime.strptime(date_str, "%b %d, %Y").date()
    else:
        book["release_date"] = None




class AsyncDBFiller:
    def __init__(self):
        self.conn_data = os.getenv("DB_CONN")
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.conn_data)

    async def disconnect(self):
        await self.pool.close()

    async def add_book(self, book, source):
        retrieve_book_fields(book)
        book["publisher"] = source
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(
                        'INSERT INTO bookinfo (author, title, release_date, genre, publisher) VALUES ($1, $2, $3, $4, $5)',
                        book["author"], book["title"], book["release_date"], book["genre"], book["publisher"]
                    )
                except BaseException as e:
                    return e
        return None


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