from sqlmodel import Session, select
from app.models import Transaction, User
from app.schemas.transaction import TransactionCreate, TransactionUpdate


class TransactionRepository:
    @staticmethod
    def create_transaction(session: Session, transaction_data: TransactionCreate) -> Transaction:
        user = session.get(User, transaction_data.user_id)
        if not user:
            raise ValueError("User not found")

        if transaction_data.type == "deposit":
            user.balance += transaction_data.amount
        elif transaction_data.type == "withdrawal":
            if user.balance < transaction_data.amount:
                raise ValueError("Insufficient balance")
            user.balance -= transaction_data.amount

        transaction = Transaction.model_validate(transaction_data)
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        return transaction

    @staticmethod
    def get_transactions(session: Session):
        transactions = session.exec(select(Transaction)).all()
        for transaction in transactions:
            transaction.user = session.get(User, transaction.user_id)
        return transactions

    @staticmethod
    def get_transaction_by_id(session: Session, transaction_id: int) -> Transaction | None:
        transaction = session.get(Transaction, transaction_id)
        if transaction:
            transaction.user = session.get(User, transaction.user_id)
        return transaction

    @staticmethod
    def update_transaction(session: Session, transaction_id: int, transaction_data: TransactionUpdate) -> Transaction | None:
        transaction = session.get(Transaction, transaction_id)
        if not transaction:
            return None

        for key, value in transaction_data.model_dump(exclude_unset=True).items():
            setattr(transaction, key, value)

        session.commit()
        session.refresh(transaction)
        return transaction

    @staticmethod
    def delete_transaction(session: Session, transaction_id: int) -> bool:
        transaction = session.get(Transaction, transaction_id)
        if not transaction:
            return False
        session.delete(transaction)
        session.commit()
        return True
