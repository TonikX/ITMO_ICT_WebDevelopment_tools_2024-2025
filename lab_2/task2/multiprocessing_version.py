from multiprocessing import Process
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from models import Task
from db import get_session, create_db_and_tables
from urls import URLS
import time

def parse_and_save(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        headings = []
        for tag in ["h1", "h2", "h3"]:
            for elem in soup.find_all(tag):
                text = elem.get_text(strip=True)
                if text:
                    headings.append(text)

        if not headings:
            headings = ["Заголовков не найдено"]

        deadline = datetime.utcnow() + timedelta(days=3)
        with get_session() as session:
            for title in headings:
                task = Task(
                    title=title[:255],
                    description=url,
                    deadline=deadline,
                    priority="high",
                    owner_id=1
                )
                session.add(task)
            session.commit()

        print(f"[Process] {url} → {', '.join(headings)}")
    except Exception as e:
        print(f"[Process] Error processing {url}: {e}")

def main():
    create_db_and_tables()
    start_time = time.time()

    processes = []
    for url in URLS:
        process = Process(target=parse_and_save, args=(url,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    duration = time.time() - start_time
    print(f"Multiprocessing {duration:.2f} seconds")

if __name__ == "__main__":
    main()
