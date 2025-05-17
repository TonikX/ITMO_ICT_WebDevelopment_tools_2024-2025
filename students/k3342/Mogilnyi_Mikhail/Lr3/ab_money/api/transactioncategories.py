from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select
from connection import get_session
from models import TransactionCategory, Transaction
from schemas import TransactionCategoryCreate, TransactionCategoryRead, TransactionCategoryBase
from api.auth import get_current_user
from models import User

router = APIRouter(prefix="/transaction-categories", tags=["Transaction Categories"])


@router.post("/", response_model=TransactionCategoryRead, status_code=status.HTTP_201_CREATED)
def create_transaction_category(
        tx_category_in: TransactionCategoryCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    tx = session.get(Transaction, tx_category_in.transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if tx.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to link to this transaction")

    db_tx_category = TransactionCategory(
        transaction_id=tx_category_in.transaction_id,
        category_id=tx_category_in.category_id,
        amount=tx_category_in.amount
    )
    session.add(db_tx_category)
    session.commit()
    session.refresh(db_tx_category)
    return db_tx_category


@router.get("/", response_model=List[TransactionCategoryRead])
def list_transaction_categories(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    stmt = select(TransactionCategory).join(Transaction).where(Transaction.user_id == current_user.id)
    tx_categories = session.exec(stmt).all()
    return tx_categories


@router.get("/{tx_category_id}", response_model=TransactionCategoryRead)
def get_transaction_category(
        tx_category_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    db_tx_category = session.get(TransactionCategory, tx_category_id)
    if not db_tx_category:
        raise HTTPException(status_code=404, detail="Transaction-category relationship not found")

    tx = session.get(Transaction, db_tx_category.transaction_id)
    if tx.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this relationship")

    return db_tx_category


@router.patch("/{tx_category_id}", response_model=TransactionCategoryRead)
def update_transaction_category(
        tx_category_id: int,
        tx_category_in: TransactionCategoryBase,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    db_tx_category = session.get(TransactionCategory, tx_category_id)
    if not db_tx_category:
        raise HTTPException(status_code=404, detail="Transaction-category relationship not found")

    tx = session.get(Transaction, db_tx_category.transaction_id)
    if tx.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this relationship")

    for field, value in tx_category_in.dict(exclude_unset=True).items():
        setattr(db_tx_category, field, value)

    session.add(db_tx_category)
    session.commit()
    session.refresh(db_tx_category)
    return db_tx_category


@router.delete("/{tx_category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction_category(
        tx_category_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    db_tx_category = session.get(TransactionCategory, tx_category_id)
    if not db_tx_category:
        raise HTTPException(status_code=404, detail="Transaction-category relationship not found")

    tx = session.get(Transaction, db_tx_category.transaction_id)
    if tx.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this relationship")

    session.delete(db_tx_category)
    session.commit()
    return None


@router.get("/transaction/{tx_id}", response_model=List[TransactionCategoryRead])
def get_categories_for_transaction(
        tx_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    tx = session.get(Transaction, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if tx.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this transaction's categories")

    stmt = select(TransactionCategory).where(TransactionCategory.transaction_id == tx_id)
    tx_categories = session.exec(stmt).all()
    return tx_categories


@router.get("/category/{category_id}", response_model=List[TransactionCategoryRead])
def get_transactions_for_category(
        category_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    stmt = select(TransactionCategory).join(Transaction).where(
        TransactionCategory.category_id == category_id,
        Transaction.user_id == current_user.id
    )
    tx_categories = session.exec(stmt).all()
    return tx_categories


