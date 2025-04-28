import threading
from typing import List

import requests
from bs4 import BeautifulSoup
from webpages.abstractions import ParserImplementation
from webpages.database import Database
from webpages.utils import ColorLog


class ThreadParser(ParserImplementation):
    def worker(self, urls: List[str], idx: int):
        local_db = Database()
        for url in urls:
            print(ColorLog.blue(f"[Thread {idx}] Parsing {url}"))
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
                title = soup.title.string if soup.title else "No Title"
                local_db.insert_page(url, title)
                print(ColorLog.blue(f"[Thread {idx}] Saved '{title}' from {url}"))
            except Exception as e:
                print(ColorLog.blue(f"[Thread {idx}] Error parsing {url}: {e}"))
        local_db.close()

    def parse_and_save_all(self, urls: List[str], num_tasks: int):
        threads = []
        chunk_size = len(urls) // num_tasks

        for i in range(num_tasks):
            chunk = urls[i * chunk_size: (i + 1) * chunk_size] if i != num_tasks - 1 else urls[i * chunk_size:]
            t = threading.Thread(target=self.worker, args=(chunk, i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
