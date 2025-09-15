import time
from multiprocessing import Pool
import requests
from bs4 import BeautifulSoup
from .config import SITES
from .database import Task, get_session, clear_tasks

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
                print(f"[Multiprocessing] Сохранено: {url} -> {title}")
            else:
                print(f"[Multiprocessing] Пропущено (уже существует): {url}")
    except requests.RequestException as e:
        print(f"[Multiprocessing] Ошибка при запросе {url}: {e}")

def run_multiprocessing():
    with Pool(processes=len(SITES)) as pool:
        pool.map(parse_and_save, SITES)

if __name__ == "__main__":
    import sys
    sys.path.append('/Users/user/Desktop/time_manager_app')  
    clear_tasks()
    start = time.time()
    run_multiprocessing()
    end = time.time()
    print(f"[Multiprocessing] Время: {end - start:.2f} секунд")