import random

import psycopg2

GENRES = [
    "fiction", "nonfiction", "mystery", "fantasy", "science_fiction", "biography",
    "history", "romance", "thriller", "children", "self_help", "poetry", "classic", "other"
]


def save_to_db(url, title, author):
    owner_id = random.randint(1, 3)
    genre = random.choice(GENRES)
    book_status = "available"
    owner_comment = url

    conn = psycopg2.connect(
        dbname="bookcrossing",
        user="nata",
        password="1",
        host="localhost",
        port=5432
    )
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO book (owner_id, title, author, genre, book_status, owner_comment)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (owner_id, title, author, genre, book_status, owner_comment)
    )
    conn.commit()
    cur.close()
    conn.close()
