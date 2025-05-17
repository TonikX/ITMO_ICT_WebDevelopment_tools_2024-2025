import os
from psycopg2 import connect
from dotenv import load_dotenv

load_dotenv()
database_uri = os.environ["DATABASE_URI"]


def get_connection():
    return connect(dsn=database_uri)


def create_book_record(title: str, author: str, isbn: str, description: str) -> None:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO books (title, author, isbn, description)
                VALUES (%s, %s, %s, %s)
                """,
                (title, author, isbn, description),
            )
        conn.commit()
    finally:
        conn.close()
