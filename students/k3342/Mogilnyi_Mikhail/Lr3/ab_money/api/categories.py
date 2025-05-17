from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from connection import get_session
from core.auth import get_current_user
from models import Category, User, TransactionCategory, Transaction
from schemas import CategoryRead

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryRead)
def create_category(
    category_in: CategoryRead,
    session: Session = Depends(get_session),
):
    db_category = Category(**category_in.dict())
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

@router.get("/", response_model=List[CategoryRead])
def list_categories(
    session: Session = Depends(get_session),
):
    categories = session.exec(select(Category)).all()
    return categories

@router.get("/{category_id}", response_model=CategoryRead)
def get_category(
    category_id: int,
    session: Session = Depends(get_session),
):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    category_in: CategoryRead,
    session: Session = Depends(get_session),
):
    db_category = session.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    updates = category_in.dict(exclude_unset=True)
    for key, val in updates.items():
        setattr(db_category, key, val)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    session: Session = Depends(get_session),
):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return {"ok": True}

from sqlalchemy import func

@router.get("/categories/summary")
def category_summary(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(
            TransactionCategory.category_id,
            func.sum(TransactionCategory.amount).label("total_amount")
        )
        .join(Transaction)
        .where(Transaction.user_id == current_user.id)
        .group_by(TransactionCategory.category_id)
    )

    results = session.exec(stmt).all()
    return [{"category_id": r[0], "total_amount": r[1]} for r in results]
