import multiprocessing
from typing import List

import requests
from bs4 import BeautifulSoup
from webpages.abstractions import ParserImplementation
from webpages.database import Database
from webpages.utils import ColorLog


class ProcessParser(ParserImplementation):
    def worker(self, urls: List[str], idx: int):
        db = Database()
        for url in urls:
            print(ColorLog.green(f"[Process {idx}] Parsing {url}"))
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")
                title = soup.title.string if soup.title else "No Title"
                db.insert_page(url, title)
                print(ColorLog.green(f"[Process {idx}] Saved '{title}' from {url}"))
            except Exception as e:
                print(ColorLog.green(f"[Process {idx}] Error parsing {url}: {e}"))
        db.close()

    def parse_and_save_all(self, urls: List[str], num_tasks: int):
        processes = []
        chunk_size = len(urls) // num_tasks

        for i in range(num_tasks):
            chunk = urls[i * chunk_size: (i + 1) * chunk_size] if i != num_tasks - 1 else urls[i * chunk_size:]
            p = multiprocessing.Process(target=self.worker, args=(chunk, i))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()
