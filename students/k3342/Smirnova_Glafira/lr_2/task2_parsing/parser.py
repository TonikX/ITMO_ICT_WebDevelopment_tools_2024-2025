from typing import Optional

import requests
from bs4 import BeautifulSoup
from sqlmodel import SQLModel, Field, Session

from students.k3342.Smirnova_Glafira.lr_2.task2_parsing.db import init_db
from students.k3342.Smirnova_Glafira.lr_2.task2_parsing.logger import logger

GENRE_URLS = [
    "https://www.livelib.ru/genre/%D0%A1%D0%BE%D0%B2%D1%80%D0%B5%D0%BC%D0%B5%D0%BD%D0%BD%D0%B0%D1%8F-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B0%D1%8F-%D0%BB%D0%B8%D1%82%D0%B5%D1%80%D0%B0%D1%82%D1%83%D1%80%D0%B0",
    "https://www.livelib.ru/genre/%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B0%D1%8F-%D0%BA%D0%BB%D0%B0%D1%81%D1%81%D0%B8%D0%BA%D0%B0",
    "https://www.livelib.ru/genre/%D0%97%D0%B0%D1%80%D1%83%D0%B1%D0%B5%D0%B6%D0%BD%D0%B0%D1%8F-%D0%BA%D0%BB%D0%B0%D1%81%D1%81%D0%B8%D0%BA%D0%B0",
    "https://www.livelib.ru/genre/%D0%97%D0%B0%D1%80%D1%83%D0%B1%D0%B5%D0%B6%D0%BD%D1%8B%D0%B5-%D0%B4%D0%B5%D1%82%D0%B5%D0%BA%D1%82%D0%B8%D0%B2%D1%8B",
    "https://www.livelib.ru/genre/%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B0%D1%8F-%D0%BB%D0%B8%D1%82%D0%B5%D1%80%D0%B0%D1%82%D1%83%D1%80%D0%B0-%D0%B4%D0%BB%D1%8F-%D0%B4%D0%B5%D1%82%D0%B5%D0%B9",
    "https://www.livelib.ru/genre/%D0%A2%D1%80%D0%B8%D0%BB%D0%BB%D0%B5%D1%80%D1%8B"
]

class BookParsed(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    author: str = Field(index=True)
    year: int
    publisher: str

def parse_genre_page(url: str, engine = None):
    try:
        if engine is None:
            engine = init_db()

        logger.info(f"Парсинг страницы: {url}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        books = []

        for book_item in soup.find_all('div', class_='book-item__inner'):
            book = parse_book(book_item)
            if book:
                books.append(book)

        with Session(engine) as session:
            session.add_all(books)
            session.commit()
            logger.info(f"Сохранено {len(books)} книг с {url}")

    except Exception as e:
        logger.error(f"Ошибка при парсинге {url}: {str(e)}")

def parse_book(book_item) -> Optional[BookParsed]:
    try:
        title_elem = book_item.find('a', class_='book-item__title')
        if not title_elem:
            logger.warning("Не найдено название книги")
            return None
        title = title_elem.text.strip()

        author_elem = book_item.find('a', class_='book-item__author')
        if not author_elem:
            logger.warning(f"Не найден автор для книги: {title}")
            return None
        author = author_elem.text.strip()

        edition_table = book_item.find('table', class_='book-item-edition')
        year = None
        publisher = None

        if edition_table:
            year_row = edition_table.find('td', string='Год издания:')
            if year_row:
                year_td = year_row.find_next_sibling('td')
                if year_td:
                    year_str = year_td.text.strip()
                    if year_str.isdigit():
                        year = int(year_str)
                    else:
                        logger.warning(f"Некорректный год издания: '{year_str}' для книги: {title}")

            publisher_row = edition_table.find('td', string='Издательство:')
            if publisher_row:
                publisher_td = publisher_row.find_next_sibling('td')
                if publisher_td:
                    publisher_link = publisher_td.find('a', class_='lists-edition__link')
                    if publisher_link:
                        publisher = publisher_link.text.strip()
                    else:
                        publisher = publisher_td.text.strip().split(',')[0].strip()

        if not all([title, author, year, publisher]):
            logger.warning(f"Неполные данные для книги '{title}'")
            return None

        return BookParsed(name=title, author=author, year=year, publisher=publisher)

    except Exception as e:
        logger.error(f"Ошибка при парсинге книги: {str(e)}", exc_info=True)
        return None