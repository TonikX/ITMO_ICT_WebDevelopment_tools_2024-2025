from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select
from app.db.session import get_session
from app.models import Budget, BudgetCategory, Category

router = APIRouter(prefix="/budgets", tags=["budgets"])

@router.post("/", response_model=Budget, status_code=status.HTTP_201_CREATED)
def create_budget(*, budget: Budget, session: Session = Depends(get_session)):
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget

@router.get("/", response_model=List[Budget])
def list_budgets(*, session: Session = Depends(get_session)):
    return session.exec(select(Budget)).all()

@router.get("/{budget_id}", response_model=Budget)
def get_budget(*, budget_id: int, session: Session = Depends(get_session)):
    b = session.get(Budget, budget_id)
    if not b:
        raise HTTPException(status_code=404, detail="Budget not found")
    return b

@router.post("/{budget_id}/categories", response_model=BudgetCategory, status_code=status.HTTP_201_CREATED)
def add_category_to_budget(*, budget_id: int, link: BudgetCategory, session: Session = Depends(get_session)):

    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    category = session.get(Category, link.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    link.budget_id = budget_id
    session.add(link)
    session.commit()
    session.refresh(link)
    return link
