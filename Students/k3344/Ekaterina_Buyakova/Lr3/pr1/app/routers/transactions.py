from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.transaction import Transaction
from models.transaction_category import TransactionCategory
from models.category import Category
from schemas.transaction import TransactionCreate, TransactionResponse
from core.jwt import get_current_user, get_db
from models.user import User
from models.budget import Budget
from sqlalchemy.sql import func


router = APIRouter()


@router.post("/", response_model=TransactionResponse)
def create_transaction(
        transaction: TransactionCreate,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    new_transaction = Transaction(
        amount=transaction.amount,
        date=transaction.date,
        description=transaction.description,
        type=transaction.type,
        user_id=user.id
    )
    db.add(new_transaction)
    db.flush()

    budget = db.query(Budget).filter(Budget.user_id == user.id, Budget.category_id == transaction.category_id).first()
    if budget:
        total_spent = db.query(func.sum(Transaction.amount)).join(TransactionCategory).filter(
            Transaction.user_id == user.id,
            TransactionCategory.category_id == transaction.category_id
        ).scalar() or 0

        if total_spent + transaction.amount > budget.limit:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Превышен бюджет по категории! Потрачено: {total_spent + transaction.amount}, лимит: {budget.limit}"
            )

    transaction_category = TransactionCategory(
        transaction_id=new_transaction.id,
        category_id=transaction.category_id,
        weight=transaction.weight
    )
    db.add(transaction_category)

    db.commit()
    db.refresh(new_transaction)

    categories = db.query(Category.name).join(TransactionCategory).filter(
        TransactionCategory.transaction_id == new_transaction.id
    ).all()

    return TransactionResponse(
        id=new_transaction.id,
        amount=new_transaction.amount,
        date=new_transaction.date,
        description=new_transaction.description,
        type=new_transaction.type,
        user_id=new_transaction.user_id,
        categories=[c[0] for c in categories]
    )


@router.get("/", response_model=list[TransactionResponse])
def get_transactions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    transactions = db.query(Transaction).filter(Transaction.user_id == user.id).all()
    return [
        TransactionResponse(
            id=t.id,
            amount=t.amount,
            date=t.date,
            description=t.description,
            type=t.type,
            user_id=t.user_id,
            categories=[tc.category.name for tc in t.categories]
        ) for t in transactions
    ]
