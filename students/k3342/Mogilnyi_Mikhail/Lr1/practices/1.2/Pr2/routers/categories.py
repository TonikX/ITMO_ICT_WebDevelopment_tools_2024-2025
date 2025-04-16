from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from models import Category
from connection import get_session
from typing import List

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/")
def create_category(category: Category, session: Session = Depends(get_session)):
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.get("/", response_model=List[Category])
def list_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()
