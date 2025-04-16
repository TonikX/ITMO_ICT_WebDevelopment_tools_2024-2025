from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from models import Transaction
from connection import get_session
from typing import List

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/")
def create_transaction(transaction: Transaction, session: Session = Depends(get_session)):
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


@router.get("/", response_model=List[Transaction])
def list_transactions(session: Session = Depends(get_session)):
    return session.exec(select(Transaction)).all()
