from fastapi import APIRouter, Depends
from sqlmodel import select, Session
from typing import List
from models.models import Budget, BudgetStats, BudgetDefault, Transaction, CategoryType, User, Account
from auth.connection import get_session
from datetime import datetime
from auth.auth import bearer_scheme

router = APIRouter(prefix="/budgets", tags=["Budgets"], dependencies=[Depends(bearer_scheme)])

@router.get("/", response_model=List[BudgetStats])
def list_budgets(session: Session = Depends(get_session)):
    budgets = session.exec(select(Budget)).all()
    result = []

    for budget in budgets:
        start_of_month = datetime(budget.year, budget.month, 1)
        end_of_month = (
            datetime(budget.year, budget.month + 1, 1)
            if budget.month < 12
            else datetime(budget.year + 1, 1, 1)
        )

        spent = 0.0

        # для всех пользователей, связанных с бюджетом
        # for user in budget.users:
        #     # для всех аккаунтов пользователя

        #     transactions = session.exec(
        #         select(Transaction)
        #         # .where(Transaction.account.has(user_id=budget.user_id))
        #         .where(Transaction.category == budget.category)
        #         .where(Transaction.date >= start_of_month)
        #         .where(Transaction.date < end_of_month)
        #     ).all()
        transactions = session.exec(
            select(Transaction)
            .join(Account)
            .where(Account.user_id.in_([user.id for user in budget.users]))
            .where(Transaction.category == budget.category)
            .where(Transaction.date >= start_of_month)
            .where(Transaction.date < end_of_month)
        ).all()


        spent = sum(t.amount for t in transactions if t.category != CategoryType.salary)

        result.append(BudgetStats(
            id=budget.id,
            users = [user.id for user in budget.users],
            # user_id=budget.user_id,
            category=budget.category,
            month=budget.month,
            year=budget.year,
            limit=budget.limit,
            spent=spent,
            remaining=max(0, budget.limit - spent)
        ))

    return result


# @router.post("/", response_model=Budget)
# def create_budget(budget: BudgetDefault, session: Session = Depends(get_session)):
#     budget = Budget.model_validate(budget)
#     session.add(budget)
#     session.commit()
#     session.refresh(budget)
#     return budget

@router.post("/", response_model=Budget)
def create_budget(budget_data: BudgetDefault, session: Session = Depends(get_session)):
    budget = Budget(
        category=budget_data.category,
        month=budget_data.month,
        year=budget_data.year,
        limit=budget_data.limit,
    )

    # добавить пользователей к бюджету
    users = session.exec(select(User).where(User.id.in_(budget_data.user_ids))).all()
    budget.users = users

    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget
