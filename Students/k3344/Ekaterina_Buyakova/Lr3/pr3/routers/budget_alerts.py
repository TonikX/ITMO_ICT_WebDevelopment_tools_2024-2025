from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from models.transaction import Transaction
from models.budget import Budget
from schemas.budget import BudgetResponse
from core.jwt import get_current_user, get_db
from models.user import User

router = APIRouter()


@router.get("/alerts", response_model=list[dict])
def get_budget_alerts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    budgets = db.query(Budget).filter(Budget.user_id == user.id).all()
    alerts = []

    for budget in budgets:
        total_spent = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.categories.any(id=budget.category_id)
        ).with_entities(func.sum(Transaction.amount)).scalar() or 0

        if total_spent >= budget.limit * 0.9:
            alerts.append({
                "category": budget.category.name,
                "spent": total_spent,
                "limit": budget.limit,
                "status": "Превышен" if total_spent > budget.limit else "Почти превышен"
            })

    return alerts
