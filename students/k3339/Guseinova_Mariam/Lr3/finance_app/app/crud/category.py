from sqlalchemy.orm import Session, joinedload
from common.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def create_category(db: Session, category: CategoryCreate):
    # Проверка на уникальность имени
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise ValueError("Category name already exists")

    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_category(db: Session, category_id: int):
    return (
        db.query(Category)
        .options(joinedload(Category.transactions))  # Подгружаем транзакции
        .filter(Category.category_id == category_id)
        .first()
    )

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Category).offset(skip).limit(limit).all()


def update_category(db: Session, category_id: int, category_data: CategoryUpdate):
    db_category = db.query(Category).filter(Category.category_id == category_id).first()
    if not db_category:
        return None

    # Проверка на уникальность при обновлении
    if category_data.name:
        existing = db.query(Category).filter(
            Category.name == category_data.name,
            Category.category_id != category_id
        ).first()
        if existing:
            raise ValueError("Category name already exists")

    for key, value in category_data.dict(exclude_unset=True).items():
        setattr(db_category, key, value)

    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int):
    db_category = db.query(Category).filter(Category.category_id == category_id).first()
    if not db_category:
        return None

    db.delete(db_category)
    db.commit()
    return True