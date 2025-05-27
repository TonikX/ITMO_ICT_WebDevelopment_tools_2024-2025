from fastapi import Depends, HTTPException, APIRouter
from typing import List
from app.connection import get_session
from app.schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate
from app.repositories.budget import BudgetRepository

router = APIRouter()


@router.post("/budget", response_model=BudgetRead)
def create_budget(budget_data: BudgetCreate, session=Depends(get_session)):
    return BudgetRepository.create_budget(session, budget_data)


@router.get("/budget_list", response_model=List[BudgetRead])
def get_budgets(session=Depends(get_session)):
    return BudgetRepository.get_budgets(session)


@router.get("/budget/{budget_id}", response_model=BudgetRead)
def get_budget_by_id(budget_id: int, session=Depends(get_session)):
    budget = BudgetRepository.get_budget_by_id(session, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@router.put("/budget/{budget_id}", response_model=BudgetRead)
def update_budget(budget_id: int, budget_data: BudgetUpdate, session=Depends(get_session)):
    budget = BudgetRepository.update_budget(session, budget_id, budget_data)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@router.delete("/budget/delete/{budget_id}")
def delete_budget(budget_id: int, session=Depends(get_session)):
    if not BudgetRepository.delete_budget(session, budget_id):
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"status": "OK"}
