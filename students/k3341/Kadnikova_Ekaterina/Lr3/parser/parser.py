import requests
from bs4 import BeautifulSoup
import re
import logging
from fake_useragent import UserAgent
from connection import get_session
from models.category import Category
import time
import random

logger = logging.getLogger(__name__)
ua = UserAgent()


def get_headers():
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }


def clean_title(title):
    if not title:
        return "No title"
    title = title.strip()
    title = re.sub(r'\s+', ' ', title)
    return title[:100]


def extract_main_content(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Удаляем ненужные элементы
    for element in soup(['script', 'style', 'nav', 'footer', 'iframe', 'noscript', 'svg']):
        element.decompose()

    # Пытаемся найти основной контент
    main_content = (soup.find('main') or
                    soup.find('article') or
                    soup.find('div', class_=re.compile(r'content|main|body', re.I)) or
                    soup.find('body'))

    return main_content.get_text(separator=' ', strip=True) if main_content else ''


def parse_finance_page(url, html=None):
    try:
        if not html:
            # Если HTML не предоставлен, загружаем страницу с обходом защиты
            response = requests.get(
                url,
                headers=get_headers(),
                timeout=10,
                allow_redirects=True
            )
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        title = clean_title(soup.title.string if soup.title else None)

        content_text = extract_main_content(html).lower()

        # Расширенный список ключевых слов
        income_keywords = {
            'income', 'revenue', 'profit', 'dividend', 'earning', 'salary', 'bonus',
            'investment', 'return', 'growth', 'yield', 'gain', 'revenue', 'cash flow',
            'capital gain', 'interest', 'royalty', 'rental', 'pension', 'annuity'
        }

        expense_keywords = {
            'expense', 'cost', 'loss', 'debt', 'spending', 'purchase', 'bill',
            'fee', 'charge', 'payment', 'outflow', 'expenditure', 'tax', 'fine',
            'penalty', 'mortgage', 'loan', 'credit', 'insurance', 'maintenance'
        }

        # Улучшенный анализ контента
        income_count = sum(content_text.count(word) for word in income_keywords)
        expense_count = sum(content_text.count(word) for word in expense_keywords)

        is_income = income_count > expense_count

        # Дополнительные проверки для сложных случаев
        if income_count == 0 and expense_count == 0:
            domain = url.split('/')[2]
            finance_domains = {
                'bloomberg', 'reuters', 'investing', 'marketwatch',
                'finance.yahoo', 'nasdaq', 'wsj', 'ft.com', 'economist'
            }
            is_income = any(fd in domain for fd in finance_domains)

        # Добавляем задержку для имитации человеческого поведения
        time.sleep(random.uniform(1, 3))

        return {
            "name": title,
            "is_income": is_income,
            "source": url
        }

    except Exception as e:
        logger.error(f"Error parsing {url}: {str(e)}", exc_info=True)
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