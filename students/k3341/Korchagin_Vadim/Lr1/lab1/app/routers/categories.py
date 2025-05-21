from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from typing import List

from db.connection import get_session
from models.finance_models import Category
from schemas.finance_schemas import CreateCategory, ReadCategory, ReadCategoryWithUsers
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=ReadCategory)
def create_category(cat: CreateCategory, session: Session = Depends(get_session)):
    new_category = Category(name=cat.name)
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    return new_category

@router.get("/", response_model=List[ReadCategory])
def get_all_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()

@router.get("/{category_id}", response_model=ReadCategoryWithUsers)
def get_category(category_id: int, session: Session = Depends(get_session)):
    stmt = (
        select(Category)
        .where(Category.id == category_id)
        .options(selectinload(Category.user_preferences))
    )
    category = session.exec(stmt).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.patch("/{category_id}", response_model=ReadCategory)
def update_category(category_id: int, data: CreateCategory, session: Session = Depends(get_session)):
    db_cat = session.get(Category, category_id)
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
    db_cat.name = data.name
    session.add(db_cat)
    session.commit()
    session.refresh(db_cat)
    return db_cat

@router.delete("/{category_id}")
def delete_category(category_id: int, session: Session = Depends(get_session)):
    db_cat = session.get(Category, category_id)
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(db_cat)
    session.commit()
    return {"ok": True}