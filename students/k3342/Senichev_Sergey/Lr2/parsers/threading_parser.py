import threading
import time
import requests
import urllib3
from bs4 import BeautifulSoup
from typing import List
from utils.db_utils import init_db, save_page

# Suppress SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def parse_and_save(url: str, session) -> None:
    """Парсит веб-страницу и сохраняет её в базу данных."""
    start_time = time.time()
    try:
        response = requests.get(url, verify=False)  # Disable SSL verification for testing
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "Заголовок не найден"
        content = soup.get_text()[:1000]  # Сохраняем первые 1000 символов
        
        end_time = time.time()
        parsing_time = end_time - start_time
        
        # Сохранение в базу данных
        save_page(
            session=session,
            url=url,
            title=title,
            content=content,
            parsing_method="threading",
            parsing_time=parsing_time
        )
        print(f"Успешно распарсено и сохранено: {url} (время: {parsing_time:.2f} сек)")
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {str(e)}")

def parse_urls(urls: List[str], num_workers: int = None) -> List[str]:
    """Парсит несколько URL с использованием потоков."""
    session = init_db()
    threads = []
    results = []
    
    # Use num_workers if provided, otherwise use the number of URLs
    worker_count = num_workers if num_workers is not None else len(urls)
    
    for url in urls:
        thread = threading.Thread(target=parse_and_save, args=(url, session))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    session.close()
    return results

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
    
    print(f"\nthreading парсер - {end_time - start_time:.2f} секунд") 