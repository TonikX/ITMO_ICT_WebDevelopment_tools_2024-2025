from sqlalchemy.orm import Session, joinedload
from common.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from common.models.tag import TransactionTag


def create_transaction(db: Session, transaction: TransactionCreate, user_id: int):
    db_transaction = Transaction(**transaction.dict(), user_id=user_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def get_transaction(db: Session, transaction_id: int):
    return db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()


def get_user_transactions(db: Session, user_id: int):
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .options(
            joinedload(Transaction.tags).joinedload(TransactionTag.tag)
        )  # Подгрузка тэгов
        .all()
    )


def update_transaction(db: Session, transaction_id: int, transaction_data: TransactionUpdate):
    db_transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not db_transaction:
        return None

    for key, value in transaction_data.dict(exclude_unset=True).items():
        setattr(db_transaction, key, value)

    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def delete_transaction(db: Session, transaction_id: int):
    db_transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not db_transaction:
        return None

    db.delete(db_transaction)
    db.commit()
    return True