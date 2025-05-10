from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from typing import List

from app.db.connection import get_session
from app.models.finance_models import Budget, User, Category
from app.schemas.finance_schemas import CreateBudget, ReadBudget, ReadBudgetFull
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/budgets", tags=["Budgets"])

@router.post("/", response_model=ReadBudget)
def create_budget(data: CreateBudget, session: Session = Depends(get_session)):
    user = session.get(User, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    cat = session.get(Category, data.category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    new_budget = Budget(
        user_id=data.user_id,
        category_id=data.category_id,
        limit_amount=data.limit_amount
    )
    session.add(new_budget)
    session.commit()
    session.refresh(new_budget)
    return new_budget

@router.get("/", response_model=List[ReadBudget])
def get_all_budgets(session: Session = Depends(get_session)):
    return session.exec(select(Budget)).all()

@router.get("/{budget_id}", response_model=ReadBudgetFull)
def get_budget(budget_id: int, session: Session = Depends(get_session)):
    stmt = (
        select(Budget)
        .where(Budget.id == budget_id)
        .options(
            selectinload(Budget.user),
            selectinload(Budget.category)
        )
    )
    db_budget = session.exec(stmt).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return db_budget

@router.patch("/{budget_id}", response_model=ReadBudget)
def update_budget(budget_id: int, data: CreateBudget, session: Session = Depends(get_session)):
    db_budget = session.get(Budget, budget_id)
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    user = session.get(User, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    cat = session.get(Category, data.category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    db_budget.user_id = data.user_id
    db_budget.category_id = data.category_id
    db_budget.limit_amount = data.limit_amount
    session.add(db_budget)
    session.commit()
    session.refresh(db_budget)
    return db_budget

@router.delete("/{budget_id}")
def delete_budget(budget_id: int, session: Session = Depends(get_session)):
    db_budget = session.get(Budget, budget_id)
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    session.delete(db_budget)
    session.commit()
    return {"ok": True}