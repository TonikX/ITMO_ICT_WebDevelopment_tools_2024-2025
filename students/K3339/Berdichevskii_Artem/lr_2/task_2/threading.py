import threading
import time
import requests
from bs4 import BeautifulSoup
from db import init_db, save_to_db


def parse_and_save(url) :
    try :
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "No title"
        save_to_db(url, title)
        print(f"[Thread] {url}: {title}")
    except Exception as e :
        print(f"[Thread] Error parsing {url}: {e}")


def main() :
    init_db()
    with open("urls.txt") as f :
        urls = [line.strip() for line in f.readlines()]

    threads = []
    start = time.time()
    for url in urls :
        t = threading.Thread(target=parse_and_save, args=(url,))
        t.start()
        threads.append(t)

    for t in threads :
        t.join()
    print(f"Threading completed in {time.time() - start:.2f}s")


if __name__ == "__main__" :
    main()
