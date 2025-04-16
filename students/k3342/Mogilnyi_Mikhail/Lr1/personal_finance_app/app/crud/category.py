from sqlmodel import Session, select
from app.models.category import Category

def get_category(session: Session, category_id: int) -> Category:
    statement = select(Category).where(Category.id == category_id)
    return session.exec(statement).first()

def get_categories(session: Session, skip: int = 0, limit: int = 100):
    statement = select(Category).offset(skip).limit(limit)
    return session.exec(statement).all()

def create_category(session: Session, category: Category) -> Category:
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

def update_category(session: Session, category: Category) -> Category:
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

def delete_category(session: Session, category: Category):
    session.delete(category)
    session.commit()
