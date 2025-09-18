from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select
from app.db.session import get_session
from app.models import Transaction, TransactionBase

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.post("/", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction(*, t: TransactionBase, session: Session = Depends(get_session)):
    transaction = Transaction.from_orm(t)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


@router.get("/", response_model=List[Transaction])
def list_transactions(*, session: Session = Depends(get_session)):
    return session.exec(select(Transaction)).all()

@router.get("/{transaction_id}", response_model=Transaction)
def get_transaction(*, transaction_id: int, session: Session = Depends(get_session)):
    tx = session.get(Transaction, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(*, transaction_id: int, session: Session = Depends(get_session)):
    tx = session.get(Transaction, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(tx)
    session.commit()
    return None
