import re
from bs4 import BeautifulSoup
import requests

def parse_books_from_url(url: str, genre: str):
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")

    books = []
    rows = soup.find_all("tr")
    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 1:
            continue

        first_td = tds[0]
        a_tag = first_td.find("a")
        font_tag = first_td.find("font")

        if not a_tag:
            continue
        title = a_tag.text.strip().strip('«»')

        author = a_tag.previous_sibling
        if author:
            author = author.strip()
        else:
            author = "Неизвестен"

        year = None
        if font_tag:
            match = re.search(r"(\d{4})", font_tag.text)
            if match:
                year = int(match.group(1))

        book = {
            "title": title,
            "author": author,
            "genre": genre,
            "published_year": year or 0
        }
        books.append(book)
    return books
