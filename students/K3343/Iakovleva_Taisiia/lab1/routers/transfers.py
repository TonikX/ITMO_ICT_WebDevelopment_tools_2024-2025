from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from models.models import Transfer, TransferDefault, Account
from auth.connection import get_session
from typing import List
from auth.auth import bearer_scheme

router = APIRouter(prefix="/transfers", tags=["Transfers"], dependencies=[Depends(bearer_scheme)])

@router.get("/", response_model=List[Transfer])
def list_transfers(session: Session = Depends(get_session)):
    return session.exec(select(Transfer)).all()

@router.post("/", response_model=Transfer)
def create_transfer(transfer: TransferDefault, session: Session = Depends(get_session)):
    if transfer.from_account_id == transfer.to_account_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same account")

    from_account = session.get(Account, transfer.from_account_id)
    to_account = session.get(Account, transfer.to_account_id)

    if not from_account or not to_account:
        raise HTTPException(status_code=404, detail="Account not found")

    if from_account.balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds in source account")

    from_account.balance -= transfer.amount
    to_account.balance += transfer.amount

    transfer = Transfer.model_validate(transfer)
    session.add(transfer)
    session.add(from_account)
    session.add(to_account)
    session.commit()
    session.refresh(transfer)
    return transfer
