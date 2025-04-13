from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.category import create_category, get_category, get_categories, update_category, delete_category
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate, CategoryOutWithTransactions
from app.database import SessionLocal
from app.auth.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter(tags=["Categories"])


@router.post("/categories", response_model=CategoryOut)
def create_new_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return create_category(db, category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/categories", response_model=list[CategoryOut])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_categories(db, skip=skip, limit=limit)

@router.get("/categories/{category_id}", response_model=CategoryOutWithTransactions)
def read_category(category_id: int, db: Session = Depends(get_db)):
    db_category = get_category(db, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.put("/categories/{category_id}", response_model=CategoryOut)
def update_existing_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        updated = update_category(db, category_id, category_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Category not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/categories/{category_id}")
def delete_existing_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"msg": "Category deleted"}