from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select
from app.db.session import get_session
from app.models import Category

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(*, category: Category, session: Session = Depends(get_session)):
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@router.get("/", response_model=List[Category])
def list_categories(*, session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()

@router.get("/{category_id}", response_model=Category)
def get_category(*, category_id: int, session: Session = Depends(get_session)):
    cat = session.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat
