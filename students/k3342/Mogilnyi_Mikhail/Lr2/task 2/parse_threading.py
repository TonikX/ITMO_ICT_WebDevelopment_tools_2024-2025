import threading
import time
import requests
from bs4 import BeautifulSoup
from saver import save_title_to_category
from db import get_session

BASE_URLS = [
    "https://rusbid.de/shops/food",
    "https://rusbid.de/shops/sports",
    "https://rusbid.de/shops/electronics"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

lock = threading.Lock()
collected_titles = []

def parse_and_collect(url: str):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.find_all('a', class_='btn-panel')

        with lock:
            for link in links:
                title = link.text.strip()
                if title:
                    collected_titles.append(title)
                    print(f"Найдена категория: {title}")
    except Exception as e:
        print(f"Ошибка при обработке {url}: {e}")

def main():
    print("Начинаем парсинг...")
    threads = []

    for url in BASE_URLS:
        thread = threading.Thread(target=parse_and_collect, args=(url,))
        threads.append(thread)
        thread.start()
        time.sleep(0.5)

    for thread in threads:
        thread.join()

    for session in get_session():
        for title in collected_titles:
            save_title_to_category(title, session)


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(f"⏱ Время выполнения: {end - start:.2f} сек.")
