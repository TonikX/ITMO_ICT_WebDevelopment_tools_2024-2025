import multiprocessing
import time
import requests
from bs4 import BeautifulSoup
from typing import List
from db_utils import init_db, save_page

def parse_and_save(url: str) -> None:
    """Парсит веб-страницу и сохраняет её в базу данных."""
    try:
        session = init_db()  # Создаем новую сессию для каждого процесса
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "Заголовок не найден"
        
        # Сохранение в базу данных
        save_page(session, url, title)
        print(f"Успешно распарсено и сохранено: {url}")
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {str(e)}")

def parse_urls(urls: List[str]) -> None:
    """Парсит несколько URL с использованием мультипроцессинга."""
    num_processes = min(multiprocessing.cpu_count(), len(urls))
    pool = multiprocessing.Pool(processes=num_processes)
    pool.map(parse_and_save, urls)
    pool.close()
    pool.join()

if __name__ == "__main__":
    # Примеры URL для парсинга
    urls = [
        "https://www.python.org",
        "https://www.github.com",
        "https://www.stackoverflow.com",
        "https://www.reddit.com",
        "https://www.wikipedia.org"
    ]
    
    start_time = time.time()
    parse_urls(urls)
    end_time = time.time()
    
    print(f"\nmultiprocessing парсер завершен за {end_time - start_time:.2f} секунд") 