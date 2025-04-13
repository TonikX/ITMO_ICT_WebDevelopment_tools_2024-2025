from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from connection import get_session
from models.user import User
from models.budget import Budget
from models.budget_category import BudgetCategory
from schemas.budget import BudgetRead, BudgetCreate, BudgetCategoryRead, BudgetUpdate
from api.auth import get_current_user
from models.transaction import Transaction
from sqlalchemy import func

router = APIRouter()

@router.post("/budgets/", response_model=BudgetRead)
def create_budget(
    budget: BudgetCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_budget = Budget(
        month=budget.month,
        user_id=current_user.id
    )
    session.add(db_budget)
    session.commit()
    session.refresh(db_budget)

    for category_id in budget.categories:
        db_budget_category = BudgetCategory(
            budget_id=db_budget.id,
            category_id=category_id,
            limit_amount=0.0
        )
        session.add(db_budget_category)

    session.commit()
    session.refresh(db_budget)
    return db_budget

@router.get("/budgets/{budget_id}", response_model=BudgetRead)
def get_budget(budget_id: int, session: Session = Depends(get_session)):
    budget = session.exec(
        select(Budget)
        .where(Budget.id == budget_id)
        .options(joinedload(Budget.categories).joinedload(BudgetCategory.category))
    ).unique().first()

    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    start_date = budget.month.replace(day=1)
    next_month = (start_date + timedelta(days=32)).replace(day=1)

    categories_with_amounts = []
    for bc in budget.categories:
        result = session.exec(
            select(func.sum(Transaction.amount))
            .where(
                Transaction.category_id == bc.category_id,
                Transaction.date >= start_date,
                Transaction.date < next_month,
            )
        ).first()
        current_amount = result or 0.0

        categories_with_amounts.append(BudgetCategoryRead(
            category_id=bc.category_id,
            limit_amount=bc.limit_amount,
            category=bc.category,
            current_amount=current_amount
        ))

    return BudgetRead(
        id=budget.id,
        user_id=budget.user_id,
        month=budget.month,
        created_at=budget.created_at,
        categories=categories_with_amounts
    )

@router.get("/budgets/", response_model=list[BudgetRead])
def get_budgets(session: Session = Depends(get_session)):
    budgets = session.exec(
        select(Budget).options(joinedload(Budget.categories).joinedload(BudgetCategory.category))
    ).unique().all()

    result = []

    for budget in budgets:
        start_date = budget.month.replace(day=1)
        next_month = (start_date + timedelta(days=32)).replace(day=1)

        categories_with_amounts = []

        for bc in budget.categories:
            current_amount = session.exec(
                select(func.sum(Transaction.amount))
                .where(
                    Transaction.category_id == bc.category_id,
                    Transaction.date >= start_date,
                    Transaction.date < next_month,
                )
            ).first() or 0.0

            categories_with_amounts.append(BudgetCategoryRead(
                category_id=bc.category_id,
                limit_amount=bc.limit_amount,
                category=bc.category,
                current_amount=current_amount
            ))

        result.append(BudgetRead(
            id=budget.id,
            user_id=budget.user_id,
            month=budget.month,
            created_at=budget.created_at,
            categories=categories_with_amounts
        ))

    return result

@router.put("/budgets/{budget_id}", response_model=BudgetRead)
def update_budget(
    budget_id: int,
    budget: BudgetUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    db_budget = session.get(Budget, budget_id)
    if not db_budget or db_budget.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Budget not found")

    db_budget.month = budget.month

    session.exec(select(BudgetCategory).where(BudgetCategory.budget_id == db_budget.id)).delete()
    session.commit()

    for category in budget.categories:
        db_budget_category = BudgetCategory(
            budget_id=db_budget.id,
            category_id=category.category_id,
            limit_amount=category.limit_amount
        )
        session.add(db_budget_category)

    session.commit()
    session.refresh(db_budget)

    return get_budget(budget_id=budget_id, session=session)

@router.delete("/budgets/{budget_id}")
def delete_budget(budget_id: int, session: Session = Depends(get_session)):
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    session.delete(budget)
    session.commit()
    return {"ok": True}

@router.get("/budgets/{budget_id}/details", response_model=BudgetRead)
def get_budget_detail(budget_id: int, session: Session = Depends(get_session)):
    budget = session.exec(
        select(Budget)
        .where(Budget.id == budget_id)
        .options(joinedload(Budget.categories).joinedload(BudgetCategory.category))
    ).unique().first()

    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    start_date = budget.month.replace(day=1)
    next_month = (start_date + timedelta(days=32)).replace(day=1)

    transactions = session.exec(
        select(Transaction)
        .where(
            Transaction.linked_object_type == "budget",
            Transaction.linked_object_id == budget.id,
            Transaction.date >= start_date,
            Transaction.date < next_month,
        )
    ).all()

    categories_with_amounts = []
    for bc in budget.categories:
        result = session.exec(
            select(func.sum(Transaction.amount))
            .where(
                Transaction.category_id == bc.category_id,
                Transaction.linked_object_type == "budget",
                Transaction.linked_object_id == budget.id,
                Transaction.date >= start_date,
                Transaction.date < next_month,
            )
        ).first()
        current_amount = result or 0.0

        categories_with_amounts.append(BudgetCategoryRead(
            category_id=bc.category_id,
            limit_amount=bc.limit_amount,
            category=bc.category,
            current_amount=current_amount
        ))

    return BudgetRead(
        id=budget.id,
        user_id=budget.user_id,
        month=budget.month,
        created_at=budget.created_at,
        categories=categories_with_amounts,
        transactions=transactions
    )