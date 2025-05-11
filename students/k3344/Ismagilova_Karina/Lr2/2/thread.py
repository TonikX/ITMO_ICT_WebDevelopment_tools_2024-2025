import time
import requests
import threading
from db import TripRealParser, SessionLocal
from parser import extract_tours_from_html, URLS

def parse_tour_page(url):
    try:
        response = requests.get(url, timeout=10)
        html = response.text
        return extract_tours_from_html(html)
    except Exception as e:
        print(f"Ошибка парсинга {url}: {e}")
        return []

def parse_and_save_threading(url):
    tours = parse_tour_page(url)
    if tours:
        with SessionLocal() as session:
            for data in tours:
                trip = TripRealParser(**data)
                session.add(trip)
            session.commit()
            print(f"Сохранено: {len(tours)} туров с {url}")

def main():
    start = time.time()

    threads = []

    for url in URLS:
        thread = threading.Thread(target=parse_and_save_threading, args=(url,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print(f"Время выполнения Threading: {time.time() - start:.7f} сек")

if __name__ == "__main__":
    main()
