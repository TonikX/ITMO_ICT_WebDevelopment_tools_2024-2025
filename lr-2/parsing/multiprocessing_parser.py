import multiprocessing
import requests
from bs4 import BeautifulSoup
import psycopg2
import time
from datetime import timedelta

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
                    (url, title, elapsed, "multiprocessing")
                )
                conn.commit()
        finally:
            conn.close()

        return {
            'url': url,
            'title': title,
            'status': 'success',
            'time_sec': round(elapsed, 2)
        }

    except Exception as e:
        return {
            'url': url,
            'title': f"Error: {str(e)}",
            'status': 'failed',
            'time_sec': 0
        }


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
    
    print(f"Starting parsing of {len(urls)} URLs using multiprocessing...")
    start_time = time.perf_counter()
    
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(parse_and_save, urls)
    
    end_time = time.perf_counter()
    total_time = end_time - start_time

    print("\nParsing complete!")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
