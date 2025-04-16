from sqlmodel import Session, select
from app.models.transaction import Transaction

def get_transaction(session: Session, transaction_id: int) -> Transaction:
    statement = select(Transaction).where(Transaction.id == transaction_id)
    return session.exec(statement).first()

def get_transactions(session: Session, skip: int = 0, limit: int = 100):
    statement = select(Transaction).offset(skip).limit(limit)
    return session.exec(statement).all()

def create_transaction(session: Session, transaction: Transaction) -> Transaction:
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction

def update_transaction(session: Session, transaction: Transaction) -> Transaction:
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction

def delete_transaction(session: Session, transaction: Transaction):
    session.delete(transaction)
    session.commit()
