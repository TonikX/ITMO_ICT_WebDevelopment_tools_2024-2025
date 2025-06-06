from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from typing import List
from models.models import Account, AccountDefault
from auth.connection import get_session
from auth.auth import bearer_scheme


router = APIRouter(prefix="/accounts", tags=["Accounts"], dependencies=[Depends(bearer_scheme)])

@router.get("/", response_model=List[Account])
def list_accounts(session: Session = Depends(get_session)):
    return session.exec(select(Account)).all()

@router.post("/", response_model=Account)
def create_account(account: AccountDefault, session: Session = Depends(get_session)):
    if account.is_goal and account.target_amount is None:
        raise HTTPException(status_code=400, detail="Goal accounts must have target_amount")

    if not account.is_goal:
        account.target_amount = None

    account = Account.model_validate(account)
    session.add(account)
    session.commit()
    session.refresh(account)
    return {"status": 200, "data": account}

@router.delete("/{account_id}")
def delete_account(account_id: int, session: Session = Depends(get_session)):
    account = session.get(Account, account_id)
    session.delete(account)
    session.commit()
    return {"ok": True}