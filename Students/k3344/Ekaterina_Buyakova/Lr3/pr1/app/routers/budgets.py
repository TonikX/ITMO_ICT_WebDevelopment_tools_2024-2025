from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Category, Budget
from schemas.budget import BudgetCreate, BudgetResponse
from core.jwt import get_current_user, get_db
from models.user import User

router = APIRouter()


@router.post("/", response_model=BudgetResponse)
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(Category.id == budget.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Категория не найдена")

    new_budget = Budget(
        limit=budget.limit,
        user_id=user.id,
        category_id=budget.category_id
    )
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    return BudgetResponse(
        id=new_budget.id,
        limit=new_budget.limit,
        user_id=new_budget.user_id,
        category_id=new_budget.category_id,
        category_name=category.name
    )


@router.get("/", response_model=list[BudgetResponse])
def get_budgets(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    budgets = db.query(Budget).filter(Budget.user_id == user.id).all()
    return [
        BudgetResponse(
            id=b.id,
            limit=b.limit,
            user_id=b.user_id,
            category_id=b.category_id,
            category_name=b.category.name
        ) for b in budgets
    ]


@router.delete("/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user.id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Бюджет не найден")

    db.delete(budget)
    db.commit()
    return {"message": "Бюджет удалён"}
