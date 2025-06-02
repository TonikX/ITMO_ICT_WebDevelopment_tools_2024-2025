import asyncio
import aiohttp
from bs4 import BeautifulSoup
from sqlmodel import Session, select, create_engine
from lr1.models.models import User, Category, Transaction, TransactionType

DATABASE_URL = "postgresql://lina:123@localhost/finance_db"
engine = create_engine(DATABASE_URL)

async def fetch(session: aiohttp.ClientSession, url: str):
    async with session.get(url) as response:
        return await response.text()

async def parse_and_save(url: str, user_id: int, category_name: str):
    try:
        async with aiohttp.ClientSession() as session:
            html = await fetch(session, url)
        soup = BeautifulSoup(html, 'html.parser')

        with Session(engine) as db_session:
            category = db_session.exec(select(Category).where(Category.name == category_name)).first()
            if not category:
                category = Category(name=category_name)
                db_session.add(category)
                db_session.commit()
                db_session.refresh(category)

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
                db_session.add(transaction)

            db_session.commit()
            print(f"Данные из {url} успешно сохранены.")
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {e}")

async def main():
    user_id = 1
    urls = [
        ("https://www.wildberries.ru/catalog/0/search.aspx?search=молоко", "Еда"),
        ("https://www.wildberries.ru/catalog/0/search.aspx?search=ноутбук", "Техника"),
        ("https://www.wildberries.ru/catalog/0/search.aspx?search=рюкзак", "Аксессуары"),
    ]

    tasks = [parse_and_save(url, user_id, category) for url, category in urls]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
