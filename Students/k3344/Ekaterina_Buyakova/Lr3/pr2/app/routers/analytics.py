from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from models.transaction import Transaction
from models import Category, TransactionCategory
from core.jwt import get_current_user, get_db
from models.user import User
from schemas.transaction import ExpenseSummaryResponse

router = APIRouter()



@router.get("/summary", response_model=list[ExpenseSummaryResponse])
def get_expense_summary(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
        start_date: datetime = Query(None),
        end_date: datetime = Query(None)
):

    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()

    results = (
        db.query(Category.name, func.sum(Transaction.amount).label("total_spent"))
        .join(TransactionCategory, TransactionCategory.category_id == Category.id)
        .join(Transaction, Transaction.id == TransactionCategory.transaction_id)
        .filter(
            Transaction.user_id == user.id,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
        .group_by(Category.name)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )

    return [{"category": category, "total_spent": total} for category, total in results]


@router.get("/top-categories", response_model=list[dict])
def get_top_expenses(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
        limit: int = 3
):

    results = (
        db.query(Category.name, func.sum(Transaction.amount).label("total_spent"))
        .join(TransactionCategory, TransactionCategory.category_id == Category.id)
        .join(Transaction, Transaction.id == TransactionCategory.transaction_id)
        .filter(Transaction.user_id == user.id)
        .group_by(Category.name)
        .order_by(func.sum(Transaction.amount).desc())
        .limit(limit)
        .all()
    )

    return [{"category": category, "total_spent": total} for category, total in results]

