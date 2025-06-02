from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.crud.transaction import create_transaction, get_user_transactions, get_transaction, delete_transaction, update_transaction
from app.schemas.transaction import TransactionCreate, TransactionOut, TransactionUpdate
from app.database import SessionLocal
from app.auth.deps import get_db, get_current_user
from common.models.user import User
from common.models.transaction import Transaction


router = APIRouter(tags=["Transactions"])


@router.post("/transactions", response_model=TransactionOut)
def create_new_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_transaction(db, transaction, current_user.user_id)

@router.get("/transactions/me", response_model=list[TransactionOut])
def get_my_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_user_transactions(db, current_user.user_id)


@router.put("/transactions/{transaction_id}", response_model=TransactionOut)
def update_existing_transaction(
        transaction_id: int,
        transaction_data: TransactionUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_transaction = get_transaction(db, transaction_id)
    if not db_transaction or db_transaction.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Transaction not found")

    updated = update_transaction(db, transaction_id, transaction_data)
    return updated


@router.delete("/transactions/{transaction_id}")
def delete_existing_transaction(
        transaction_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_transaction = get_transaction(db, transaction_id)
    if not db_transaction or db_transaction.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Transaction not found")

    delete_transaction(db, transaction_id)
    return {"msg": "Transaction deleted"}


@router.get("/transactions/{transaction_id}", response_model=TransactionOut)
def get_single_transaction(
        transaction_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_transaction = (
        db.query(Transaction)
        .options(joinedload(Transaction.category))
        .filter(Transaction.transaction_id == transaction_id)
        .first()
    )
    if not db_transaction or db_transaction.user_id != current_user.user_id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction