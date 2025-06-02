import threading
import requests
from bs4 import BeautifulSoup
from sqlmodel import Session, select
from lr1.models.models import User, Category, Transaction, TransactionType
from sqlmodel import SQLModel, Session, create_engine


DATABASE_URL = "postgresql://lina:123@localhost/finance_db"
engine = create_engine(DATABASE_URL)

def parse_and_save(url: str, user_id: int, category_name: str):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        with Session(engine) as session:
            category = session.exec(select(Category).where(Category.name == category_name)).first()
            if not category:
                category = Category(name=category_name)
                session.add(category)
                session.commit()
                session.refresh(category)

            products = soup.select("div.product-card__main")[:5]
            for product in products:
                title = product.select_one("span.goods-name").text.strip()
                price_tag = product.select_one("ins.lower-price")
                amount = float(price_tag.text.replace('₽', '').replace(' ', '').strip()) if price_tag else 0.0

                transaction = Transaction(
                    amount=amount,
                    transaction_type=TransactionType.EXPENSE,
                    date="2025-06-01",
                    user_id=user_id,
                    category_id=category.id,
                    link=url,
                )
                session.add(transaction)

            session.commit()
            print(f"Данные из {url} успешно сохранены.")
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {e}")

def main():
    user_id = 1
    urls = [
        ("https://www.wildberries.ru/catalog/0/search.aspx?search=молоко", "Еда"),
        ("https://www.wildberries.ru/catalog/0/search.aspx?search=ноутбук", "Техника"),
        ("https://www.wildberries.ru/catalog/0/search.aspx?search=рюкзак", "Аксессуары"),
    ]

    threads = []
    for url, category in urls:
        thread = threading.Thread(target=parse_and_save, args=(url, user_id, category))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
