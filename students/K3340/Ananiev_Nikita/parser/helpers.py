from bs4 import BeautifulSoup
from datetime import datetime, date
from database import BookInfoParsed

tpl = "/ebooks/search/?sort_order=downloads&start_index={}"
base = "https://www.gutenberg.org"


def parse_book_links(html):
    soup = BeautifulSoup(html, "html.parser")
    book_list = soup.find_all("li", class_="booklink")
    return [base + book.a["href"] for book in book_list]


def parse_book_details(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"id": "about_book_table"})
    if not table:
        return None
    details = BookInfoParsed(title="", author="", release_date=date.today(), genre="")
    for row in table.find_all("tr"):
        th, td = row.find("th"), row.find("td")
        if not th:
            continue
        inner = (td.text if not td.a else td.a.text).strip()
        field = "_".join(th.text.lower().split())
        if hasattr(details, field):
            if field == "release_date":
                inner = datetime.strptime(inner, '%b %d, %Y').date()
            setattr(details, field, inner)
        if field == "subject":
            details.genre = inner
    return details
