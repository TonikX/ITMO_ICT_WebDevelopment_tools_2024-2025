from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from app.database import get_session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.crud.category import get_category, get_categories, create_category, update_category, delete_category

router = APIRouter()

@router.get("/", response_model=list[CategoryRead])
def read_categories(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    categories = get_categories(session, skip, limit)
    return categories

@router.get("/{category_id}", response_model=CategoryRead)
def read_category(category_id: int, session: Session = Depends(get_session)):
    category = get_category(session, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=CategoryRead)
def create_new_category(category: CategoryCreate, session: Session = Depends(get_session)):
    db_category = Category(**category.dict())
    created = create_category(session, db_category)
    return created

@router.put("/{category_id}", response_model=CategoryRead)
def update_existing_category(category_id: int, category_update: CategoryUpdate, session: Session = Depends(get_session)):
    db_category = get_category(session, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    update_data = category_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    updated = update_category(session, db_category)
    return updated

@router.delete("/{category_id}")
def delete_existing_category(category_id: int, session: Session = Depends(get_session)):
    db_category = get_category(session, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    delete_category(session, db_category)
    return {"detail": "Category deleted"}
