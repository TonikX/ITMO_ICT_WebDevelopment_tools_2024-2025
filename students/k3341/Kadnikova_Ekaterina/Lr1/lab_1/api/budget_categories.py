from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from connection import get_session
from models.budget_category import BudgetCategory
from schemas.budget import BudgetCategoryRead

router = APIRouter()

@router.get("/budget-categories/", response_model=list[BudgetCategoryRead])
def get_all_budget_categories(db: Session = Depends(get_session)):
    return db.query(BudgetCategory).all()

@router.get("/budget-categories/{id}", response_model=BudgetCategoryRead)
def get_budget_category(id: int, db: Session = Depends(get_session)):
    bc = db.get(BudgetCategory, id)
    if not bc:
        raise HTTPException(status_code=404, detail="Not found")
    return bc

@router.delete("/budget-categories/{id}")
def delete_budget_category(id: int, db: Session = Depends(get_session)):
    bc = db.get(BudgetCategory, id)
    if not bc:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(bc)
    db.commit()
    return {"ok": True}