import dotenv
import asyncpg
import os
from pydantic import BaseModel
from datetime import date

dotenv.load_dotenv()

class LoggingConnection(asyncpg.Connection):
    async def execute(self, query: str, *args, **kwargs):
        print(f"[SQL] {query}, args={args}")
        return await super().execute(query, *args, **kwargs)


class BookInfoParsed(BaseModel):
    title: str
    author: str
    release_date: date
    publisher: str | None = None
    genre: str


class AsyncDBFiller:
    def __init__(self):
        self.conn_data = os.getenv("DB_CONN")
        print(self.conn_data)
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.conn_data)

    async def disconnect(self):
        await self.pool.close()

    async def add_book(self, book: BookInfoParsed, source: str = "unknown"):
        if book is None:
            raise ValueError("Book cannot be None")
        book.publisher = source
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(
                        """INSERT INTO "bookinfo" (title, author, release_date, genre, publisher) VALUES ($1, $2, $3, $4, $5)""",
                        *vars(book).values()
                    )
                except BaseException as e:
                    return e
        return None
