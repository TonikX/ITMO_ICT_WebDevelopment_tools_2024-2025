from datetime import datetime
import asyncpg
import psycopg2

def prepare_book_record(raw: dict, source: str) -> tuple:
    title = raw.get("title","").strip()
    author = raw.get("author","").strip()
    date_str = raw.get("release_date","")
    try:
        rd = datetime.strptime(date_str,"%b %d, %Y").date() if date_str else None
    except ValueError:
        rd = None
    genre = raw.get("subject","").strip()
    return author, title, rd, genre, source

class AsyncDBFiller:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: asyncpg.Pool | None = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn)

    async def disconnect(self):
        await self.pool.close()

    async def add_book(self, raw: dict, source: str) -> bool:
        rec = prepare_book_record(raw, source)
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO bookinfo(author,title,release_date,genre,publisher)
                VALUES($1,$2,$3,$4,$5) ON CONFLICT DO NOTHING
            """, *rec)
        return True

class SyncDBFiller:
    def __init__(self, dsn: str):
        self.conn = psycopg2.connect(dsn)
    def add_book(self, raw: dict, source: str) -> bool:
        rec = prepare_book_record(raw, source)
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO bookinfo(author,title,release_date,genre,publisher)
                    VALUES(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING
                """, rec)
            self.conn.commit()
            return True
        except:
            self.conn.rollback()
            return False
    def disconnect(self):
        self.conn.close()