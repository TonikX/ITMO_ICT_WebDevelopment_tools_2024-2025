from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import Category, User
from app.connections import get_session
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=Category)
def create_category(category: Category, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    category.user_id = user.id
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@router.get("/", response_model=list[Category])
def get_user_categories(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    statement = select(Category).where(Category.user_id == user.id)
    return session.exec(statement).all()

@router.get("/{category_id}", response_model=Category)
def get_category(category_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    category = session.get(Category, category_id)
    if not category or category.user_id != user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/{category_id}", response_model=Category)
def update_category(category_id: int, updated: Category, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    category = session.get(Category, category_id)
    if not category or category.user_id != user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in updated.dict(exclude_unset=True).items():
        setattr(category, field, value)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@router.delete("/{category_id}")
def delete_category(category_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    category = session.get(Category, category_id)
    if not category or category.user_id != user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return {"ok": True}