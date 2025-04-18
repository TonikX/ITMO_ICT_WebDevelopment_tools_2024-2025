from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import Budget, Category, User
from app.connections import get_session
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.post("/", response_model=Budget)
def create_budget(budget: Budget, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    category = session.get(Category, budget.category_id)
    if not category or category.user_id != user.id:
        raise HTTPException(status_code=400, detail="Invalid category for this user")

    budget.user_id = user.id
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget


@router.get("/", response_model=list[Budget])
def get_budgets(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    statement = select(Budget).where(Budget.user_id == user.id)
    return session.exec(statement).all()


@router.get("/{budget_id}", response_model=Budget)
def get_budget(budget_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    budget = session.get(Budget, budget_id)
    if not budget or budget.user_id != user.id:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@router.put("/{budget_id}", response_model=Budget)
def update_budget(budget_id: int, updated: Budget, session: Session = Depends(get_session),
                  user: User = Depends(get_current_user)):
    budget = session.get(Budget, budget_id)
    if not budget or budget.user_id != user.id:
        raise HTTPException(status_code=404, detail="Budget not found")

    if updated.category_id:
        category = session.get(Category, updated.category_id)
        if not category or category.user_id != user.id:
            raise HTTPException(status_code=400, detail="Invalid category for this user")

    for field, value in updated.dict(exclude_unset=True).items():
        setattr(budget, field, value)

    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget


@router.delete("/{budget_id}")
def delete_budget(budget_id: int, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    budget = session.get(Budget, budget_id)
    if not budget or budget.user_id != user.id:
        raise HTTPException(status_code=404, detail="Budget not found")

    session.delete(budget)
    session.commit()
    return {"ok": True}