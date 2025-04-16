from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from app.database import get_session
from app.models.budget import Budget
from app.schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate
from app.crud.budget import get_budget, get_budgets, create_budget, update_budget, delete_budget

router = APIRouter()

@router.get("/", response_model=list[BudgetRead])
def read_budgets(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    budgets = get_budgets(session, skip, limit)
    return budgets

@router.get("/{budget_id}", response_model=BudgetRead)
def read_budget(budget_id: int, session: Session = Depends(get_session)):
    budget = get_budget(session, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget

@router.post("/", response_model=BudgetRead)
def create_new_budget(budget: BudgetCreate, session: Session = Depends(get_session)):
    db_budget = Budget(**budget.dict())
    created = create_budget(session, db_budget)
    return created

@router.put("/{budget_id}", response_model=BudgetRead)
def update_existing_budget(budget_id: int, budget_update: BudgetUpdate, session: Session = Depends(get_session)):
    db_budget = get_budget(session, budget_id)
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    update_data = budget_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_budget, key, value)
    updated = update_budget(session, db_budget)
    return updated

@router.delete("/{budget_id}")
def delete_existing_budget(budget_id: int, session: Session = Depends(get_session)):
    db_budget = get_budget(session, budget_id)
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    delete_budget(session, db_budget)
    return {"detail": "Budget deleted"}
