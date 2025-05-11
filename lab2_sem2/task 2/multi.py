from multiprocessing import Pool
import requests
from bs4 import BeautifulSoup
from db import get_session
from models import Trip


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
        content_div = soup.find('div', class_='mw-parser-output')
        if content_div:
            for p in content_div.find_all('p'):
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
        print(f"[Process] {destination} сохранена.")
    except Exception as e:
        print(f"[Process Error] {url}: {e}")


def handle_url_multi(chunk):
    for url in chunk:
        parse_and_save(url)


def main():
    urls = load_urls("urls.txt")
    num_processes = 5
    chunk_size = len(urls) // num_processes
    chunks = [urls[i * chunk_size: (i + 1) * chunk_size] for i in range(num_processes - 1)]
    chunks.append(urls[(num_processes - 1) * chunk_size:])

    with Pool(processes=num_processes) as pool:
        pool.map(handle_url_multi, chunks)


if __name__ == "__main__":
    import time

    start = time.time()
    main()
    print(f"Время выполнения: {time.time() - start:.2f} сек")
