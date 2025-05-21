from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from db.connection import get_session
from models.finance_models import UserCategoryPreference, User, Category
from schemas.finance_schemas import CreateUserCategoryPreference, ReadUserCategoryPreference

router = APIRouter(prefix="/preferences", tags=["Preferences"])

@router.post("/", response_model=ReadUserCategoryPreference)
def create_pref(data: CreateUserCategoryPreference, session: Session = Depends(get_session)):
    user = session.get(User, data.user_id)
    cat = session.get(Category, data.category_id)
    if not user or not cat:
        raise HTTPException(status_code=404, detail="User or category not found")

    pref = UserCategoryPreference(**data.dict())
    session.add(pref)
    session.commit()
    session.refresh(pref)
    return pref

@router.get("/", response_model=List[ReadUserCategoryPreference])
def get_all(session: Session = Depends(get_session)):
    return session.exec(select(UserCategoryPreference)).all()

@router.get("/{user_id}/{category_id}", response_model=ReadUserCategoryPreference)
def get_one(user_id: int, category_id: int, session: Session = Depends(get_session)):
    pref = session.get(UserCategoryPreference, (user_id, category_id))
    if not pref:
        raise HTTPException(status_code=404, detail="Not found")
    return pref

@router.delete("/{user_id}/{category_id}")
def delete_pref(user_id: int, category_id: int, session: Session = Depends(get_session)):
    pref = session.get(UserCategoryPreference, (user_id, category_id))
    if not pref:
        raise HTTPException(status_code=404, detail="Not found")
    session.delete(pref)
    session.commit()
    return {"ok": True}
