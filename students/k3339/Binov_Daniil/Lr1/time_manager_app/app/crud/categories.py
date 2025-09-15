from sqlmodel import Session, select
from typing import Optional, List
from app.models import Category
from app.schemas import CategoryCreate, CategoryRead

def create_category(session: Session, category: CategoryCreate) -> Category:
    db_category = Category(**category.dict())
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

def get_category(session: Session, category_id: int) -> Optional[Category]:
    return session.get(Category, category_id)

def get_categories(session: Session) -> List[Category]:
    statement = select(Category)
    return session.exec(statement).all()

def update_category(session: Session, category_id: int, category_update: dict) -> Optional[Category]:
    db_category = get_category(session, category_id)
    if not db_category:
        return None
    for key, value in category_update.items():
        setattr(db_category, key, value)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

def delete_category(session: Session, category_id: int) -> bool:
    db_category = get_category(session, category_id)
    if not db_category:
        return False
    session.delete(db_category)
    session.commit()
    return True