from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from app.database import get_session
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from app.crud.transaction import get_transaction, get_transactions, create_transaction, update_transaction, delete_transaction

router = APIRouter()

@router.get("/", response_model=list[TransactionRead])
def read_transactions(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    transactions = get_transactions(session, skip, limit)
    return transactions

@router.get("/{transaction_id}", response_model=TransactionRead)
def read_transaction(transaction_id: int, session: Session = Depends(get_session)):
    transaction = get_transaction(session, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.post("/", response_model=TransactionRead)
def create_new_transaction(transaction: TransactionCreate, session: Session = Depends(get_session)):
    db_transaction = Transaction(**transaction.dict())
    created = create_transaction(session, db_transaction)
    return created

@router.put("/{transaction_id}", response_model=TransactionRead)
def update_existing_transaction(transaction_id: int, transaction_update: TransactionUpdate, session: Session = Depends(get_session)):
    db_transaction = get_transaction(session, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    update_data = transaction_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_transaction, key, value)
    updated = update_transaction(session, db_transaction)
    return updated

@router.delete("/{transaction_id}")
def delete_existing_transaction(transaction_id: int, session: Session = Depends(get_session)):
    db_transaction = get_transaction(session, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    delete_transaction(session, db_transaction)
    return {"detail": "Transaction deleted"}
