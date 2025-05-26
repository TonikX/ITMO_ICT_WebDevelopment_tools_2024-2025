from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import Transaction, User, Category
from app.connections import get_session
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=Transaction)
def create_transaction(transaction: Transaction, session: Session = Depends(get_session),
                       user: User = Depends(get_current_user)):
    # Проверим, что категория принадлежит пользователю
    category = session.get(Category, transaction.category_id)
    if not category or category.user_id != user.id:
        raise HTTPException(status_code=400, detail="Invalid category for this user")

    transaction.user_id = user.id
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


@router.get("/", response_model=list[Transaction])
def get_transactions(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    statement = select(Transaction).where(Transaction.user_id == user.id)
    return session.exec(statement).all()


@router.get("/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: int, session: Session = Depends(get_session),
                    user: User = Depends(get_current_user)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction or transaction.user_id != user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.put("/{transaction_id}", response_model=Transaction)
def update_transaction(transaction_id: int, updated: Transaction, session: Session = Depends(get_session),
                       user: User = Depends(get_current_user)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction or transaction.user_id != user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Если категория меняется — проверим, что она user's
    if updated.category_id:
        category = session.get(Category, updated.category_id)
        if not category or category.user_id != user.id:
            raise HTTPException(status_code=400, detail="Invalid category for this user")

    for field, value in updated.dict(exclude_unset=True).items():
        setattr(transaction, field, value)

    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, session: Session = Depends(get_session),
                       user: User = Depends(get_current_user)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction or transaction.user_id != user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")

    session.delete(transaction)
    session.commit()
    return {"ok": True}