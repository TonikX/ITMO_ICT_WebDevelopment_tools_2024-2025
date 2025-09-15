import time
import threading
import requests
from bs4 import BeautifulSoup
from task2.config import SITES, CHUNKS, CHUNK_SIZE
from task2.database import Task, get_session, clear_tasks

def parse_and_save(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else "No title"
        with get_session() as session:
            existing = session.query(Task).filter(Task.description == url).first()
            if not existing:
                task = Task(title=title, description=url, user_id=1)
                session.add(task)
                session.commit()
                print(f"[Threading] Сохранено: {url} -> {title}")
            else:
                print(f"[Threading] Пропущено (уже существует): {url}")
    except requests.RequestException as e:
        print(f"[Threading] Ошибка при запросе {url}: {e}")

def run_threads():
    threads = []
    for i in range(CHUNKS):
        start_idx = i * CHUNK_SIZE
        end_idx = min(start_idx + CHUNK_SIZE, len(SITES))
        chunk_urls = SITES[start_idx:end_idx]
        for url in chunk_urls:
            thread = threading.Thread(target=parse_and_save, args=(url,))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    import sys
    sys.path.append('/Users/user/Desktop/time_manager_app')  
    clear_tasks()
    start = time.time()
    run_threads()
    end = time.time()
    print(f"[Threading] Время: {end - start:.2f} секунд")