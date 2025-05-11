import time
import requests
import multiprocessing
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

def parse_and_save(url):
    tours = parse_tour_page(url)
    with SessionLocal() as session:
        for data in tours:
            trip = TripRealParser(**data)
            session.add(trip)
        session.commit()
        print(f"Сохранено: {len(tours)} туров с {url}")

def main():
    start = time.time()

    processes = []

    for url in URLS:
        process = multiprocessing.Process(target=parse_and_save, args=(url,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    print(f"Время выполнения Multiprocessing: {time.time() - start:.7f} сек")

if __name__ == "__main__":
    main()
