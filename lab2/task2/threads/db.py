import os
from psycopg2.pool import ThreadedConnectionPool
from dotenv import load_dotenv


load_dotenv()
database_uri = os.environ["DATABASE_URI"]

pool = ThreadedConnectionPool(minconn=1, maxconn=10, dsn=database_uri)


def create_book_record(title: str, author: str, isbn: str, description: str) -> None:
    conn = pool.getconn()
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
        pool.putconn(conn)
