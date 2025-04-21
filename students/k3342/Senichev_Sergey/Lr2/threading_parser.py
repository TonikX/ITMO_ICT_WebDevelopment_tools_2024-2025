import threading
import time
import requests
from bs4 import BeautifulSoup
from typing import List
from db_utils import init_db, save_page

def parse_and_save(url: str, session) -> None:
    """Парсит веб-страницу и сохраняет её в базу данных."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "Заголовок не найден"
        
        # Сохранение в базу данных
        save_page(session, url, title)
        print(f"Успешно распарсено и сохранено: {url}")
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {str(e)}")

def parse_urls(urls: List[str]) -> None:
    """Парсит несколько URL с использованием потоков."""
    session = init_db()
    threads = []
    
    for url in urls:
        thread = threading.Thread(target=parse_and_save, args=(url, session))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

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
    
    print(f"\nthreading парсер завершен за {end_time - start_time:.2f} секунд") 