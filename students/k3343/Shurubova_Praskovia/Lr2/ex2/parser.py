from bs4 import BeautifulSoup
from model import RealBook
import logging
from typing import Optional

logging.basicConfig(filename="parser.log", level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)


def parse_genre_page(html: str) -> list[RealBook]:
    try:
        soup = BeautifulSoup(html, 'html.parser')
        books = []

        for book_item in soup.find_all('div', class_='book-item__inner'):
            book = parse_book(book_item)
            if book:
                books.append(book)

        logger.info(f"Найдено {len(books)} книг на странице")
        return books

    except Exception as e:
        logger.error(f"Ошибка при парсинге HTML: {str(e)}", exc_info=True)
        return []


def parse_book(book_item) -> Optional[RealBook]:
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

        description_div = book_item.find('div', class_='book-item-desc')
        description = description_div.find('p').text.strip() if description_div and description_div.find('p') else "Описание недоступно"

        if not all([title, author, year, publisher]):
            logger.warning(f"Неполные данные для книги '{title}'")
            return None

        return RealBook(
            name=title,
            author=author,
            year=year,
            publisher=publisher,
            description=description
        )

    except Exception as e:
        logger.error(f"Ошибка при парсинге книги: {str(e)}", exc_info=True)
        return None
