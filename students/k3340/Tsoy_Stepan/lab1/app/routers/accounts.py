from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select
from app.db.session import get_session
from app.models import Account

router = APIRouter(prefix="/accounts", tags=["accounts"])

class AccountCreate(Account):
    pass

@router.post("/", response_model=Account, status_code=status.HTTP_201_CREATED)
def create_account(*, account_in: AccountCreate, session: Session = Depends(get_session)):
    account = Account.from_orm(account_in)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

@router.get("/", response_model=List[Account])
def list_accounts(*, session: Session = Depends(get_session)):
    return session.exec(select(Account)).all()

@router.get("/{account_id}", response_model=Account)
def get_account(*, account_id: int, session: Session = Depends(get_session)):
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.patch("/{account_id}", response_model=Account)
def update_account(*, account_id: int, account_in: Account, session: Session = Depends(get_session)):
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    account_data = account_in.dict(exclude_unset=True)
    for key, val in account_data.items():
        setattr(account, key, val)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(*, account_id: int, session: Session = Depends(get_session)):
    acc = session.get(Account, account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    session.delete(acc)
    session.commit()
    return None
