from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from models import Budget
from connection import get_session
from typing import List

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.post("/")
def create_budget(budget: Budget, session: Session = Depends(get_session)):
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget


@router.get("/", response_model=List[Budget])
def list_budgets(session: Session = Depends(get_session)):
    return session.exec(select(Budget)).all()
