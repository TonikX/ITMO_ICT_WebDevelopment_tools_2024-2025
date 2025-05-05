
from threading import Thread
import requests
from bs4 import BeautifulSoup
import psycopg2
import time

def parse_and_save(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string

    conn = psycopg2.connect("dbname=finance_db user=postgres password=12345678 host=localhost")
    cur = conn.cursor()

    cur.execute("INSERT INTO threading (url, title) VALUES (%s, %s)", (url, title))
    conn.commit()

    print(f"Заголовок {url}: {title}")

    cur.close()
    conn.close()

def main():
    urls = ["https://ostrovok.ru/", "https://www.avito.ru/", "https://www.cian.ru/"]
    threads = []

    for url in urls:
        thread = Thread(target=parse_and_save, args=(url,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Время выполнения: {execution_time} секунд(ы)")