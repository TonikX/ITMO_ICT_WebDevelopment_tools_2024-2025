from models import Category
from sqlmodel import Session, select

def save_title_to_category(title: str, session: Session):
    stmt = select(Category).where(Category.name == title)
    result = session.exec(stmt).first()

    if not result:
        new_cat = Category(name=title)
        session.add(new_cat)
        session.commit()
        session.refresh(new_cat)
        print(f"Сохранена новая категория: {title}")
    else:
        print(f"Категория уже существует: {title}")
