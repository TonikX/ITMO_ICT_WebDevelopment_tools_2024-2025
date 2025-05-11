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
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504]
            )
            session = requests.Session()
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            self.queue.put(session)

    def get_session(self):
        return self.queue.get()

    def put_session(self, session):
        self.queue.put(session)


def parse_book_links(html):
    soup = BeautifulSoup(html, "html.parser")
    book_list = soup.find_all("li", class_="booklink")
    return [base + book.a["href"] for book in book_list]


def parse_book_details(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"id": "about_book_table"})
    details = dict()
    for row in table.find_all("tr"):
        th, td = row.find("th"), row.find("td")
        if not th:
            continue
        inner = td.text if not td.a else td.a.text
        field = "_".join(th.text.lower().split())
        details.setdefault(field, inner.strip())
    return details
