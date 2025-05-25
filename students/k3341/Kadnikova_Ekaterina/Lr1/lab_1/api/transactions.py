from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from connection import get_session
from models.budget import Budget
from models.goal import Goal
from models.transaction import Transaction, LinkedObjectType
from schemas.transaction import TransactionRead, TransactionCreate, TransactionType, TransactionUpdate
from api.auth import get_current_user
from models.user import User

router = APIRouter()

@router.post("/transactions/", response_model=TransactionRead)
def create_transaction(
    tr: TransactionCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Проверка
    if bool(tr.linked_object_id) != bool(tr.linked_object_type):
        raise HTTPException(
            status_code=400,
            detail="Both linked_object_id and linked_object_type must be set together."
        )

    db_tr = Transaction(**tr.dict(), user_id=current_user.id)
    db.add(db_tr)
    db.commit()
    db.refresh(db_tr)

    if tr.linked_object_type == LinkedObjectType.goal:
        goal = db.get(Goal, tr.linked_object_id)
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        if tr.type == TransactionType.expense:
            goal.current_amount -= tr.amount
        elif tr.type == TransactionType.income:
            goal.current_amount += tr.amount
        db.add(goal)

    elif tr.linked_object_type == LinkedObjectType.budget:
        budget = db.get(Budget, tr.linked_object_id)
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        if not hasattr(budget, "current_amount"):
            setattr(budget, "current_amount", Decimal(0))
        if tr.type == TransactionType.expense:
            budget.current_amount += tr.amount
        elif tr.type == TransactionType.income:
            budget.current_amount -= tr.amount
        db.add(budget)

    db.commit()
    return db_tr

@router.get("/transactions/", response_model=list[TransactionRead])
def get_transactions(db: Session = Depends(get_session)):
    return db.query(Transaction).all()

@router.get("/transactions/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: int, db: Session = Depends(get_session)):
    tr = db.get(Transaction, transaction_id)
    if not tr:
        raise HTTPException(status_code=404, detail="Not found")
    return tr

@router.patch("/transactions/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    update_data: TransactionUpdate = Body(...),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    tr = db.get(Transaction, transaction_id)
    if not tr:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if tr.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    old_amount = tr.amount
    old_type = tr.type
    old_linked_type = tr.linked_object_type
    old_linked_id = tr.linked_object_id

    update_dict = update_data.dict(exclude_unset=True)

    for field, value in update_dict.items():
        setattr(tr, field, value)

    db.add(tr)

    if old_linked_type == LinkedObjectType.goal:
        goal = db.get(Goal, old_linked_id)
        if goal:
            if old_type == TransactionType.income:
                goal.current_amount -= old_amount
            elif old_type == TransactionType.expense:
                goal.current_amount += old_amount
            db.add(goal)

    elif old_linked_type == LinkedObjectType.budget:
        budget = db.get(Budget, old_linked_id)
        if budget:
            if old_type == TransactionType.income:
                budget.current_amount += old_amount
            elif old_type == TransactionType.expense:
                budget.current_amount -= old_amount
            db.add(budget)

    if tr.linked_object_type == LinkedObjectType.goal:
        goal = db.get(Goal, tr.linked_object_id)
        if not goal:
            raise HTTPException(status_code=404, detail="Linked goal not found")
        if tr.type == TransactionType.income:
            goal.current_amount += tr.amount
        elif tr.type == TransactionType.expense:
            goal.current_amount -= tr.amount
        db.add(goal)

    elif tr.linked_object_type == LinkedObjectType.budget:
        budget = db.get(Budget, tr.linked_object_id)
        if not budget:
            raise HTTPException(status_code=404, detail="Linked budget not found")
        if not hasattr(budget, "current_amount"):
            setattr(budget, "current_amount", Decimal(0))
        if tr.type == TransactionType.income:
            budget.current_amount -= tr.amount
        elif tr.type == TransactionType.expense:
            budget.current_amount += tr.amount
        db.add(budget)

    db.commit()
    db.refresh(tr)
    return tr

@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_session)):
    tr = db.get(Transaction, transaction_id)
    if not tr:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(tr)
    db.commit()
    return {"ok": True}