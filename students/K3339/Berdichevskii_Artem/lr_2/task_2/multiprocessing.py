from multiprocessing import Process
import time
import requests
from bs4 import BeautifulSoup
from db import init_db, save_to_db

class URLProcessor:
    def __init__(self, urls_file="urls.txt"):
        self.urls_file = urls_file

    def parse_and_save(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string.strip() if soup.title else "No title"
            save_to_db(url, title)
            print(f"[Process] {url}: {title}")
        except Exception as e:
            print(f"[Process] Error parsing {url}: {e}")

    def process_urls(self):
        init_db()
        with open(self.urls_file) as f:
            urls = [line.strip() for line in f.readlines()]

        processes = []
        start = time.time()
        for url in urls:
            p = Process(target=self.parse_and_save, args=(url,))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()
        print(f"Multiprocessing completed in {time.time() - start:.2f}s")

if __name__ == "__main__":
    processor = URLProcessor()
    processor.process_urls()