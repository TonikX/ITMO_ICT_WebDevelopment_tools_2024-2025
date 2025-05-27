from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session
from typing import List

from app.connection import get_session
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from app.repositories.transaction import TransactionRepository

router = APIRouter()


@router.post("/transaction", response_model=TransactionRead)
def create_transaction(transaction_data: TransactionCreate, session: Session = Depends(get_session)):
    try:
        return TransactionRepository.create_transaction(session, transaction_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions", response_model=List[TransactionRead])
def get_transactions(session: Session = Depends(get_session)):
    return TransactionRepository.get_transactions(session)


@router.get("/transaction/{transaction_id}", response_model=TransactionRead)
def get_transaction_by_id(transaction_id: int, session: Session = Depends(get_session)):
    transaction = TransactionRepository.get_transaction_by_id(session, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.put("/transaction/{transaction_id}", response_model=TransactionRead)
def update_transaction(transaction_id: int, transaction_data: TransactionUpdate, session: Session = Depends(get_session)):
    transaction = TransactionRepository.update_transaction(session, transaction_id, transaction_data)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.delete("/transaction/{transaction_id}")
def delete_transaction(transaction_id: int, session: Session = Depends(get_session)):
    if not TransactionRepository.delete_transaction(session, transaction_id):
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"status": "OK"}