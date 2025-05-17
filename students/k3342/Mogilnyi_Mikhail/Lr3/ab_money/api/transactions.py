from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from connection import get_session
from models import Transaction, TransactionCategory
from schemas import TransactionCreate, TransactionRead, CategoryRead
from api.auth import get_current_user
from models import User

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    tx_in: TransactionCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_tx = Transaction(
        **tx_in.model_dump(exclude_unset=True),
        user_id=current_user.id
    )
    session.add(db_tx)
    session.commit()
    session.refresh(db_tx)

    if tx_in.category_ids:
        links = [
            TransactionCategory(
                transaction_id=db_tx.id,
                category_id=cid,
                amount=db_tx.amount / len(tx_in.category_ids)
            )
            for cid in tx_in.category_ids
        ]
        session.add_all(links)
        session.commit()
        session.refresh(db_tx)

    return TransactionRead(
        id=db_tx.id,
        user_id=db_tx.user_id,
        amount=db_tx.amount,
        description=db_tx.description,
        type=db_tx.type,
        categories=[link.category_id for link in db_tx.categories],
    )


@router.get("/", response_model=List[TransactionRead])
def list_transactions(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result: List[TransactionRead] = []
    txs = session.exec(select(Transaction).where(Transaction.user_id == current_user.id)).all()
    for tx in txs:
        result.append(TransactionRead(
            id=tx.id,
            user_id=tx.user_id,
            amount=tx.amount,
            description=tx.description,
            type=tx.type,
            categories=[link.category_id for link in tx.categories],
        ))
    return result

@router.get("/{tx_id}", response_model=TransactionRead)
def get_transaction(
    tx_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_tx = session.get(Transaction, tx_id)
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if db_tx.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this transaction")
    return TransactionRead(
        id=db_tx.id,
        user_id=db_tx.user_id,
        amount=db_tx.amount,
        description=db_tx.description,
        type=db_tx.type,
        categories=[link.category_id for link in db_tx.categories],
    )


@router.patch("/{tx_id}", response_model=TransactionRead)
def update_transaction(
        tx_id: int,
        tx_in: TransactionCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    db_tx = session.get(Transaction, tx_id)
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if db_tx.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this transaction")

    for field, val in tx_in.dict(exclude_unset=True, exclude={"category_ids"}).items():
        setattr(db_tx, field, val)
    session.add(db_tx)
    session.commit()

    existing_links = session.exec(
        select(TransactionCategory)
        .where(TransactionCategory.transaction_id == tx_id)
    ).all()

    for link in existing_links:
        session.delete(link)

    # Then add new category links
    for cid in tx_in.category_ids:
        link = TransactionCategory(
            transaction_id=tx_id,
            category_id=cid,
            amount=db_tx.amount,
        )
        session.add(link)

    session.commit()
    session.refresh(db_tx)

    return TransactionRead(
        id=db_tx.id,
        user_id=db_tx.user_id,
        amount=db_tx.amount,
        description=db_tx.description,
        type=db_tx.type,
        categories=[link.category_id for link in db_tx.categories],
    )

@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    tx_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_tx = session.get(Transaction, tx_id)
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if db_tx.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this transaction")
    session.delete(db_tx)
    session.commit()
    return None


@router.get("/with-categories/details", response_model=List[TransactionRead])
def get_transactions_with_categories(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .options(
            selectinload(Transaction.categories).selectinload(TransactionCategory.category)
        )
    )

    transactions = session.exec(stmt).all()

    result = []
    for tx in transactions:
        result.append(TransactionRead(
            id=tx.id,
            user_id=tx.user_id,
            amount=tx.amount,
            description=tx.description,
            type=tx.type,
            categories=[
                CategoryRead(
                    id=tc.category.id,
                    name=tc.category.name
                ) for tc in tx.categories
            ]
        ))
    return result

