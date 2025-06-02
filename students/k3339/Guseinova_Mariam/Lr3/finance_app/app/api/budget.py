from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.budget import create_budget, get_user_budgets, delete_budget, update_budget, get_budget
from app.schemas.budget import BudgetCreate, BudgetOut, BudgetUpdate
from app.database import SessionLocal
from app.auth.deps import get_db, get_current_user
from common.models.user import User
from common.models.budget import Budget

router = APIRouter(tags=["Budgets"])


@router.post("/budgets", response_model=BudgetOut)
def create_new_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_budget(db, budget, current_user.user_id)

@router.get("/budgets/me", response_model=list[BudgetOut])
def get_my_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_budgets(db, current_user.user_id)

@router.get("/budgets/{budget_id}", response_model=BudgetOut)
def get_single_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_budget = get_budget(db, budget_id)
    if not db_budget or db_budget.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Budget not found")
    return db_budget

@router.put("/budgets/{budget_id}", response_model=BudgetOut)
def update_budget_endpoint(
        budget_id: int,
        budget_data: BudgetUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_budget = db.query(Budget).filter(Budget.budget_id == budget_id).first()
    if not db_budget or db_budget.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Budget not found")

    updated_budget = update_budget(db, budget_id, budget_data)
    return updated_budget


@router.delete("/budgets/{budget_id}")
def delete_budget_endpoint(
        budget_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_budget = db.query(Budget).filter(Budget.budget_id == budget_id).first()
    if not db_budget or db_budget.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Budget not found")

    delete_budget(db, budget_id)
    return {"msg": "Budget deleted"}