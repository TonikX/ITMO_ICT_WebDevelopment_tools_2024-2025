import re
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from task2.common.db import save_hackathon


def extract_year_from_url(url):
    match = re.search(r'/search/(\d{4})|/theme/.+?/(\d{4})', url)
    if match:
        year = match.group(1) or match.group(2)
        return int(year)
    return None


def parse_hackathon_card(card, year):
    try:
        title_tag = card.select_one("a.ht-event-card__title")
        title = title_tag.text.strip() if title_tag else "No Title"

        date_tag = card.select_one("div.ht-event-card__date")
        date_text = date_tag.text.strip() if date_tag else None

        start_date = None
        if date_text:
            try:
                date_text = date_text.split('-')[0].strip()
                start_date = datetime.strptime(f"{date_text} {year}", "%d %b %Y")
            except Exception as e:
                print(f"Не удалось распарсить дату '{date_text}': {e}")

        desc_tag = card.select_one("div.ht-event-card__desc")
        description = desc_tag.text.strip() if desc_tag else "No description."

        return {
            "name": title,
            "description": description,
            "start_date": start_date or datetime.now(),
            "end_date": (start_date + timedelta(days=1)) if start_date else datetime.now(),
        }
    except Exception as e:
        print(f"[ERROR] Ошибка при парсинге карточки: {e}")
        return None


def process_page(url, html):
    soup = BeautifulSoup(html, "html.parser")
    year = extract_year_from_url(url) or datetime.now().year
    cards = soup.select("div.ht-event-card__content")

    for card in cards:
        data = parse_hackathon_card(card, year)
        if data:
            save_hackathon(data)
