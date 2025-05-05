import multiprocessing
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

def parse_url(url: str):
    titles = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', class_='btn-panel')

        for link in links:
            title = link.text.strip()
            if title:
                titles.append(title)
                print(f"🔍 [PID {multiprocessing.current_process().pid}] Найдена категория: {title}")
    except Exception as e:
        print(f"Ошибка при обработке {url}: {e}")
    return titles

def main():

    with multiprocessing.Pool(processes=min(4, len(BASE_URLS))) as pool:
        results = pool.map(parse_url, BASE_URLS)

    all_titles = [title for sublist in results for title in sublist]

    for session in get_session():
        for title in all_titles:
            save_title_to_category(title, session)

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(f"Время выполнения: {end - start:.2f} сек.")
