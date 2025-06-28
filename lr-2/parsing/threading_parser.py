import threading
import requests
from bs4 import BeautifulSoup
import psycopg2
import time

DB_CONFIG = {
    'host': 'localhost',
    'database': 'web_parsing',
    'user': 'postgres',
    'password': 'postgres'
}

def init_db():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pages (
                    id SERIAL PRIMARY KEY,
                    url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    execution_time FLOAT NOT NULL,
                    method TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    finally:
        conn.close()

def parse_and_save(url):
    try:
        start_time = time.perf_counter()

        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else 'No title'

        end_time = time.perf_counter()
        elapsed = end_time - start_time

        conn = psycopg2.connect(**DB_CONFIG)
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    'INSERT INTO pages (url, title, execution_time, method) VALUES (%s, %s, %s, %s)',
                    (url, title, elapsed, "threading")
                )
                conn.commit()
        finally:
            conn.close()

        print(f"Processed: {url} | Time: {elapsed:.2f}s | Method: threading")

    except Exception as e:
        print(f"Failed to process {url}: {e}")

def main():
    init_db()
    
    urls = [
        'https://my.itmo.ru',
        'https://www.github.com',
        'https://www.stackoverflow.com',
        'https://www.wikipedia.org',
        'https://www.youtube.com',
        'https://isu.ifmo.ru',
    ]
    threads = []
    for url in urls:
        thread = threading.Thread(target=parse_and_save, args=(url,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Threading parsing complete!")

if __name__ == "__main__":
    main()
