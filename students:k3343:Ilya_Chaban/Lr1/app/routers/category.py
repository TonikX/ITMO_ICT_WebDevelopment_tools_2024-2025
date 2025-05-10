from fastapi import Depends, HTTPException, APIRouter
from typing import List
from app.connection import get_session
from app.models import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead
from app.repositories.category import CategoryRepository

router = APIRouter()


@router.post("/category", response_model=CategoryRead)
def create_category(category_data: CategoryCreate, session=Depends(get_session)):
    return CategoryRepository.create_category(session, category_data)


@router.get("/category_list", response_model=List[CategoryRead])
def get_categories(session=Depends(get_session)):
    return CategoryRepository.get_categories(session)


@router.get("/category/{category_id}", response_model=CategoryRead)
def get_category_by_id(category_id: int, session=Depends(get_session)):
    category = CategoryRepository.get_category_by_id(session, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/category/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, category_data: CategoryUpdate, session=Depends(get_session)):
    category = CategoryRepository.update_category(session, category_id, category_data)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/category/delete/{category_id}")
def delete_category(category_id: int, session=Depends(get_session)):
    if not CategoryRepository.delete_category(session, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"status": "OK"}
