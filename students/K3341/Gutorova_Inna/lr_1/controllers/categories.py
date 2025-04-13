from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from models import TaskCategory, TaskCategoryCreate, TaskCategoryRead
from connection import get_session
from auth.auth import auth_service
from models import User

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=TaskCategoryRead)
def create_category(
        category: TaskCategoryCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    db_category = TaskCategory(**category.dict(), user_id=current_user.id)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@router.get("/", response_model=List[TaskCategoryRead])
def read_categories(
        skip: int = 0,
        limit: int = 100,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    categories = session.exec(
        select(TaskCategory)
        .where(TaskCategory.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    ).all()
    return categories


@router.get("/{category_id}", response_model=TaskCategoryRead)
def read_category(
        category_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    category = session.get(TaskCategory, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.patch("/{category_id}", response_model=TaskCategoryRead)
def update_category(
        category_id: int,
        category: TaskCategoryCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    db_category = session.get(TaskCategory, category_id)
    if not db_category or db_category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")

    category_data = category.dict(exclude_unset=True)
    for key, value in category_data.items():
        setattr(db_category, key, value)

    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@router.delete("/{category_id}")
def delete_category(
        category_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(auth_service.get_current_user)
):
    category = session.get(TaskCategory, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(category)
    session.commit()
    return {"message": "Category deleted successfully"}