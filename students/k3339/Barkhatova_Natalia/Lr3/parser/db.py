import random
import asyncpg

GENRES = [
    "fiction", "nonfiction", "mystery", "fantasy", "science_fiction", "biography",
    "history", "romance", "thriller", "children", "self_help", "poetry", "classic", "other"
]


async def save_to_db(url, title, author):
    owner_id = random.randint(1, 3)
    genre = random.choice(GENRES)
    book_status = "available"
    owner_comment = url

    conn = await asyncpg.connect(
        user='nata',
        password='1',
        database='bookcrossing',
        host='postgres_db',
        port=5432
    )
    try:
        await conn.execute(
            """
            INSERT INTO book (owner_id, title, author, genre, book_status, owner_comment)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            owner_id, title, author, genre, book_status, owner_comment
        )
    finally:
        await conn.close()
