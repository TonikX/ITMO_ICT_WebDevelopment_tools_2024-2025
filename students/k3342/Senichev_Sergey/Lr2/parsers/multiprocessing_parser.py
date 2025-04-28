import multiprocessing
import time
import requests
import urllib3
from bs4 import BeautifulSoup
from typing import List
from utils.db_utils import init_db, save_page

# Suppress SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def parse_and_save(url: str) -> None:
    """Парсит веб-страницу и сохраняет её в базу данных."""
    start_time = time.time()
    try:
        session = init_db()  # Создаем новую сессию для каждого процесса
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
            parsing_method="multiprocessing",
            parsing_time=parsing_time
        )
        print(f"Успешно распарсено и сохранено: {url} (время: {parsing_time:.2f} сек)")
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {str(e)}")
    finally:
        session.close()

def parse_urls(urls: List[str], num_workers: int = None) -> List[str]:
    """Парсит несколько URL с использованием мультипроцессинга."""
    # Use num_workers if provided, otherwise use the number of CPUs
    if num_workers is None:
        num_workers = min(multiprocessing.cpu_count(), len(urls))
    
    pool = multiprocessing.Pool(processes=num_workers)
    pool.map(parse_and_save, urls)
    pool.close()
    pool.join()
    
    return []  # Return empty list for consistency with other parsers

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
    
    print(f"\nmultiprocessing парсер - {end_time - start_time:.2f} секунд") 