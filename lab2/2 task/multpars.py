import multiprocessing
import time
import requests
from bs4 import BeautifulSoup
import sqlite3


def parse_and_save(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        title_tag = soup.find('title')
        title = title_tag.text.strip() if title_tag else f"Без заголовка - {url}"

        conn = sqlite3.connect('pages.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO pages (url, title) VALUES (?, ?)', (url, title))
        conn.commit()
        conn.close()

        print(f"Сохранено: {title}")
        return title
    except Exception as e:
        print(f"Ошибка для {url}: {e}")
        return None


def main():
    conn = sqlite3.connect('pages.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS pages 
                     (id INTEGER PRIMARY KEY, url TEXT, title TEXT)''')
    conn.commit()
    conn.close()

    urls = [
        'https://httpbin.org/html',
        'https://httpbin.org/json',
        'https://jsonplaceholder.typicode.com/',
        'https://httpbin.org/status/200',
        'https://httpbin.org/headers',
        'https://httpbin.org/ip',
        'https://httpbin.org/user-agent',
        'https://httpbin.org/delay/1'
    ]

    start_time = time.time()

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.map(parse_and_save, urls)

    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time:.2f} секунд")
    print(f"Количество процессов: {multiprocessing.cpu_count()}")


if __name__ == "__main__":
    main()