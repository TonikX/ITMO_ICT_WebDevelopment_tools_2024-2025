from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from app.connection import get_session
from app.crud.categories import create_category, get_category, get_categories, update_category, delete_category
from app.schemas import CategoryCreate, CategoryRead
from app.routers.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=CategoryRead)
def create_new_category(category: CategoryCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return create_category(session, category)

@router.get("/{category_id}", response_model=CategoryRead)
def read_category(category_id: int, session: Session = Depends(get_session)):
    db_category = get_category(session, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category  

@router.get("/", response_model=List[CategoryRead])
def read_categories(session: Session = Depends(get_session)):
    return get_categories(session)

@router.put("/{category_id}", response_model=CategoryRead)
def update_existing_category(category_id: int, category_update: dict, session: Session = Depends(get_session)):
    updated_category = update_category(session, category_id, category_update)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category

@router.delete("/{category_id}")
def delete_existing_category(category_id: int, session: Session = Depends(get_session)):
    if not delete_category(session, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted"}