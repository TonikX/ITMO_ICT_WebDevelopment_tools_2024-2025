from bs4 import BeautifulSoup
import re
import logging

from connection import get_session
from models.category import Category

logger = logging.getLogger(__name__)


def clean_title(title):
    if not title:
        return "No title"
    title = title.strip()
    title = re.sub(r'\s+', ' ', title)
    return title[:100]


def extract_main_content(html):
    soup = BeautifulSoup(html, 'html.parser')

    for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'noscript']):
        element.decompose()

    main_content = soup.find('main') or soup.find('article') or soup.find('div',
                                                                          class_=lambda x: x and 'content' in x.lower())

    return main_content.get_text(separator=' ', strip=True) if main_content else soup.get_text(separator=' ',
                                                                                               strip=True)


def parse_finance_page(url, html):
    try:
        soup = BeautifulSoup(html, 'html.parser')
        title = clean_title(soup.title.string if soup.title else None)

        content_text = extract_main_content(html).lower()

        income_keywords = {
            'income', 'revenue', 'profit', 'dividend', 'earning',
            'investment', 'return', 'growth', 'yield', 'gain'
        }
        expense_keywords = {
            'expense', 'cost', 'loss', 'debt', 'spending',
            'fee', 'charge', 'payment', 'outflow', 'expenditure'
        }

        income_count = sum(1 for word in income_keywords if word in content_text)
        expense_count = sum(1 for word in expense_keywords if word in content_text)

        is_income = income_count > expense_count

        if income_count == 0 and expense_count == 0:
            domain = url.split('/')[2]
            finance_domains = {'invest', 'market', 'nasdaq', 'bloomberg', 'finance', 'stock'}
            is_income = any(fd in domain for fd in finance_domains)

        return {
            "name": title,
            "is_income": is_income,
            "source": url
        }

    except Exception as e:
        logger.error(f"Error parsing {url}: {str(e)}")
        return None


def save_category(data):
    if not data:
        return

    db = next(get_session())
    try:
        existing = db.query(Category).filter_by(name=data["name"]).first()
        if not existing:
            category = Category(
                name=data["name"],
                is_income=data["is_income"]
            )
            db.add(category)
            db.commit()
            logger.info(f"Saved category: {data['name']} (Source: {data['source']})")
        else:
            logger.info(f"Category already exists: {data['name']}")
    except Exception as e:
        logger.error(f"Error saving category {data['name']}: {str(e)}")
        db.rollback()
    finally:
        db.close()