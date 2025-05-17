from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select, delete
from connection import get_session
from models import Budget, BudgetCategoryLink, User
from schemas import BudgetCreate, BudgetRead, BudgetCategoryBase
from api.auth import get_current_user

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.post("/", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
def create_budget(
        budget_in: BudgetCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    try:
        db_budget = Budget(
            name=budget_in.name,
            period_start=budget_in.period_start,
            period_end=budget_in.period_end,
            user_id=current_user.id,
        )
        session.add(db_budget)
        session.commit()
        session.refresh(db_budget)

        for item in budget_in.planned:
            link = BudgetCategoryLink(
                budget_id=db_budget.id,
                category_id=item.category_id,
                planned_amount=item.planned_amount,
            )
            session.add(link)
        session.commit()
        session.refresh(db_budget)

        planned = [
            BudgetCategoryBase(
                category_id=item.category_id,
                planned_amount=item.planned_amount
            )
            for item in budget_in.planned
        ]

        return BudgetRead(
            id=db_budget.id,
            name=db_budget.name,
            period_start=db_budget.period_start,
            period_end=db_budget.period_end,
            planned=planned,
            user_id=db_budget.user_id,
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[BudgetRead])
def list_budgets(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    budgets = session.exec(
        select(Budget).where(Budget.user_id == current_user.id)
    ).all()

    result = []
    for budget in budgets:
        planned = [
            BudgetCategoryBase(
                category_id=link.category_id,
                planned_amount=link.planned_amount
            )
            for link in budget.category_links
        ]
        result.append(BudgetRead(
            id=budget.id,
            name=budget.name,
            period_start=budget.period_start,
            period_end=budget.period_end,
            planned=planned,
            user_id=budget.user_id,
        ))
    return result


@router.get("/{budget_id}", response_model=BudgetRead)
def get_budget(
        budget_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    if budget.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this budget")

    planned = [
        BudgetCategoryBase(
            category_id=link.category_id,
            planned_amount=link.planned_amount
        )
        for link in budget.category_links
    ]

    return BudgetRead(
        id=budget.id,
        name=budget.name,
        period_start=budget.period_start,
        period_end=budget.period_end,
        planned=planned,
        user_id=budget.user_id,
    )


@router.patch("/{budget_id}", response_model=BudgetRead)
def update_budget(
        budget_id: int,
        budget_in: BudgetCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    db_budget = session.get(Budget, budget_id)
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    if db_budget.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this budget")

    updates = budget_in.dict(exclude_unset=True, exclude={"planned"})
    for key, val in updates.items():
        setattr(db_budget, key, val)
    session.add(db_budget)
    session.commit()

    if budget_in.planned is not None:
        session.exec(
            delete(BudgetCategoryLink)
            .where(BudgetCategoryLink.budget_id == budget_id)
        )

        for item in budget_in.planned:
            link = BudgetCategoryLink(
                budget_id=budget_id,
                category_id=item.category_id,
                planned_amount=item.planned_amount,
            )
            session.add(link)
        session.commit()

    session.refresh(db_budget)

    planned = [
        BudgetCategoryBase(
            category_id=link.category_id,
            planned_amount=link.planned_amount
        )
        for link in db_budget.category_links
    ]

    return BudgetRead(
        id=db_budget.id,
        name=db_budget.name,
        period_start=db_budget.period_start,
        period_end=db_budget.period_end,
        planned=planned,
        user_id=db_budget.user_id,
    )


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
        budget_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    if budget.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this budget")

    session.delete(budget)
    session.commit()
    return None


@router.get("/public/all", response_model=List[BudgetRead])
def list_all_budgets_public(
        session: Session = Depends(get_session),
):
    budgets = session.exec(select(Budget)).all()

    result = []
    for budget in budgets:
        planned = [
            BudgetCategoryBase(
                category_id=link.category_id,
                planned_amount=link.planned_amount
            )
            for link in budget.category_links
        ]
        result.append(BudgetRead(
            id=budget.id,
            name=budget.name,
            period_start=budget.period_start,
            period_end=budget.period_end,
            planned=planned,
            user_id=budget.user_id,
        ))
    return result