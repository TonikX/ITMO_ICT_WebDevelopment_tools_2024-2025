from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from typing import List
from sqlalchemy.orm import selectinload

from app.db.connection import get_session
from app.models.finance_models import Account, User
from app.schemas.finance_schemas import CreateAccount, ReadAccount, ReadAccountWithTransactions

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.post("/", response_model=ReadAccount)
def create_account(account_data: CreateAccount, session: Session = Depends(get_session)):
    user = session.get(User, account_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    account = Account(
        user_id=account_data.user_id,
        name=account_data.name,
        balance=account_data.balance
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

@router.get("/", response_model=List[ReadAccount])
def get_all_accounts(session: Session = Depends(get_session)):
    return session.exec(select(Account)).all()

@router.get("/{account_id}", response_model=ReadAccountWithTransactions)
def get_account(account_id: int, session: Session = Depends(get_session)):
    stmt = (
        select(Account)
        .where(Account.id == account_id)
        .options(selectinload(Account.transactions))
    )
    db_acc = session.exec(stmt).first()
    if not db_acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_acc

@router.patch("/{account_id}", response_model=ReadAccount)
def update_account(account_id: int, acc_data: CreateAccount, session: Session = Depends(get_session)):
    db_acc = session.get(Account, account_id)
    if not db_acc:
        raise HTTPException(status_code=404, detail="Account not found")

    user = session.get(User, acc_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_acc.user_id = acc_data.user_id
    db_acc.name = acc_data.name
    db_acc.balance = acc_data.balance

    session.add(db_acc)
    session.commit()
    session.refresh(db_acc)
    return db_acc

@router.delete("/{account_id}")
def delete_account(account_id: int, session: Session = Depends(get_session)):
    db_acc = session.get(Account, account_id)
    if not db_acc:
        raise HTTPException(status_code=404, detail="Account not found")
    session.delete(db_acc)
    session.commit()
    return {"ok": True}