import threading
import requests
from bs4 import BeautifulSoup
from db import get_session
from models import Trip
import time


def load_urls(filename):
    with open(filename, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def parse_and_save(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title_element = soup.find('h1', id='firstHeading')
        destination = title_element.get_text(strip=True) if title_element else "Неизвестно"

        description = ""
        for p in soup.find('div', class_='mw-parser-output').find_all('p'):
            text = p.get_text(strip=True)
            if text:
                description += text + " "
                if len(description) > 1000:
                    break
        if not description.strip():
            description = "Описание отсутствует."

        with get_session() as session:
            session.add(Trip(destination=destination, description=description))
            session.commit()
        print(f"[Thread] {destination} сохранена.")

    except Exception as e:
        print(f"[Thread Error] {url}: {e}")


def handle_url_threading(chunk):
    for url in chunk:
        parse_and_save(url)


def main():
    urls = load_urls("urls.txt")
    num_threads = 5
    step = len(urls) // num_threads
    threads = []

    for i in range(num_threads):
        start = i * step
        end = len(urls) if i == num_threads - 1 else (i + 1) * step
        t = threading.Thread(target=handle_url_threading, args=(urls[start:end],))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    start = time.time()
    main()
    print(f"Время выполнения: {time.time() - start:.2f} сек")
