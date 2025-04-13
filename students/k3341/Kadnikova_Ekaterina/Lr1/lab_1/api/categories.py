from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from connection import get_session
from models.category import Category
from schemas.category import CategoryRead, CategoryCreate, CategoryUpdate

router = APIRouter()

@router.post("/categories/", response_model=CategoryRead)
def create_category(cat: CategoryCreate, db: Session = Depends(get_session)):
    db_cat = Category(**cat.dict())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.get("/categories/", response_model=list[CategoryRead])
def get_categories(db: Session = Depends(get_session)):
    return db.query(Category).all()

@router.get("/categories/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_session)):
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Not found")
    return cat

@router.put("/categories/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    cat_update: CategoryUpdate,
    db: Session = Depends(get_session)
):
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    if cat_update.name:
        cat.name = cat_update.name

    if cat_update.is_income:
        cat.income = cat_update.income

    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_session)):
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(cat)
    db.commit()
    return {"ok": True}