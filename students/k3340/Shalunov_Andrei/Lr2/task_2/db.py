import os
from datetime import datetime
import dotenv
import asyncpg
import psycopg2

dotenv.load_dotenv()

def prepare_book_record(raw: dict, source: str) -> tuple:
    title = raw.get("title", "").strip()
    author = raw.get("author", "").strip()
    date_str = raw.get("release_date", "")
    genre = raw.get("subject", "").strip()
    try:
        release_date = datetime.strptime(date_str, "%b %d, %Y").date() if date_str else None
    except ValueError:
        release_date = None
    return author, title, release_date, genre, source

class AsyncDBFiller:
    def __init__(self):
        self.dsn = os.getenv("DB_CONN")
        self.pool: asyncpg.Pool | None = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn)

    async def disconnect(self):
        assert self.pool
        await self.pool.close()

    async def add_book(self, raw: dict, source: str) -> bool:
        author, title, release_date, genre, publisher = prepare_book_record(raw, source)
        assert self.pool
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO bookinfo(author, title, release_date, genre, publisher)
                VALUES($1,$2,$3,$4,$5)
                ON CONFLICT DO NOTHING
            """, author, title, release_date, genre, publisher)
        return True

class SyncDBFiller:
    def __init__(self, lock=None):
        self.conn = psycopg2.connect(os.getenv("DB_CONN"))
        self.lock = lock

    def disconnect(self):
        self.conn.close()

    def add_book(self, raw: dict, source: str) -> bool:
        author, title, release_date, genre, publisher = prepare_book_record(raw, source)
        if self.lock:
            self.lock.acquire()
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO bookinfo(author, title, release_date, genre, publisher)
                    VALUES (%s,%s,%s,%s,%s)
                    ON CONFLICT DO NOTHING
                """, (author, title, release_date, genre, publisher))
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            return False
        finally:
            if self.lock:
                self.lock.release()
        return True