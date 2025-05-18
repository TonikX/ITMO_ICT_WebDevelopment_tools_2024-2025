import threading
import time
import requests
from bs4 import BeautifulSoup

from db_thr import create_user_record

BASE_URL = "https://itmo.ru"
LETTERS = [
    "/ru/personlist/192/letter_192.htm",
    "/ru/personlist/193/letter_193.htm",
    "/ru/personlist/194/letter_194.htm",
    "/ru/personlist/195/letter_195.htm",
    "/ru/personlist/196/letter_196.htm",
]

def parse_and_save(path: str):
    url = BASE_URL + path
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        people_links = soup.select("a.contact-pad.-person-list")
        for person_link in people_links:
            name_tag = person_link.select_one("h4.name")
            if name_tag:
                full_name = name_tag.get_text(strip=True)
                if full_name:
                    create_user_record(full_name)
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
    except Exception as e:
        print(f"Error parsing {url}: {e}")

def worker(path: str, results: list, index: int):
    results[index] = parse_and_save(path)

if __name__ == "__main__":
    threads = []
    results = [None] * len(LETTERS)

    t0 = time.perf_counter()
    for i, letter_path in enumerate(LETTERS):
        thread = threading.Thread(target=worker, args=(letter_path, results, i))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    t1 = time.perf_counter()

    print(f"Threading parsing duration: {t1 - t0:.2f} seconds")
