import os
import psycopg2
from contextlib import contextmanager

DB_URL = "postgresql://postgres:admin1@localhost:5432/financedb"

@contextmanager
def get_conn():
    conn = psycopg2.connect(DB_URL)
    try:
        yield conn
    finally:
        conn.close()

def save_title_to_db(title: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO category (name, is_income) VALUES (%s, %s)",
                (title, False)
            )
        conn.commit()