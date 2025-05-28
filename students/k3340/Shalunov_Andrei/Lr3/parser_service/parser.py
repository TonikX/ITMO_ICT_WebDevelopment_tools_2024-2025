from bs4 import BeautifulSoup
import requests
import queue
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

tpl = "/ebooks/search/?sort_order=downloads&start_index={}"
base = "https://www.gutenberg.org"

class SessionPool:
    def __init__(self, size=10):
        self.queue = queue.Queue(maxsize=size)
        for _ in range(size):
            retry = Retry(total=3, backoff_factor=1, status_forcelist=[500,502,503,504])
            s = requests.Session()
            adapter = HTTPAdapter(max_retries=retry)
            s.mount("http://", adapter)
            s.mount("https://", adapter)
            self.queue.put(s)

    def get_session(self): return self.queue.get()
    def put_session(self, s): self.queue.put(s)

def parse_book_links(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all("li", class_="booklink")
    return [base + it.a["href"] for it in items if it.a and it.a.get("href")]

def parse_book_details(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", id="about_book_table")
    if not table:
        return {}
    details = {}
    for row in table.find_all("tr"):
        th, td = row.find("th"), row.find("td")
        if not th or not td:
            continue
        key = "_".join(th.get_text(strip=True).lower().split())
        val = td.a.get_text(strip=True) if td.a else td.get_text(strip=True)
        details[key] = val
    return details