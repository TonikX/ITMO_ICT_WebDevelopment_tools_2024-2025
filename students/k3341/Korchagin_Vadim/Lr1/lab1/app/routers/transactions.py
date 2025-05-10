from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from typing import List

from app.db.connection import get_session
from app.models.finance_models import Transaction, User, Category, Account
from app.schemas.finance_schemas import CreateTransaction, ReadTransaction, ReadTransactionFull
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=ReadTransaction)
def create_transaction(
    trans: CreateTransaction, 
    session: Session = Depends(get_session)
):
    """
    Создаём новую транзакцию и, если указан account_id, 
    автоматически меняем баланс счёта (account.balance).
    """
    user = session.get(User, trans.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cat = session.get(Category, trans.category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    new_trans = Transaction(
        user_id=trans.user_id,
        category_id=trans.category_id,
        account_id=trans.account_id,
        amount=trans.amount,
        description=trans.description
    )

    session.add(new_trans)

    # Если транзакция привязана к счёту — меняем баланс
    if trans.account_id is not None:
        account = session.get(Account, trans.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        account.balance += trans.amount
        session.add(account)

    session.commit()
    session.refresh(new_trans)
    return new_trans


@router.get("/", response_model=List[ReadTransaction])
def get_all_transactions(session: Session = Depends(get_session)):
    return session.exec(select(Transaction).order_by(Transaction.created_at.desc())).all()


@router.get("/{transaction_id}", response_model=ReadTransactionFull)
def get_transaction(transaction_id: int, session: Session = Depends(get_session)):
    stmt = (
        select(Transaction)
        .where(Transaction.id == transaction_id)
        .options(
            selectinload(Transaction.user),
            selectinload(Transaction.category),
            selectinload(Transaction.account)
        )
    )
    db_trans = session.exec(stmt).first()
    if not db_trans:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_trans


@router.patch("/{transaction_id}", response_model=ReadTransaction)
def update_transaction(
    transaction_id: int, 
    data: CreateTransaction, 
    session: Session = Depends(get_session)
):
    """
    Частично обновляем транзакцию.  
    1) Возвращаем старую сумму в баланс старого счёта (если был).  
    2) Привязываем к новому счёту и добавляем в его баланс новую сумму.  
    """
    db_trans = session.get(Transaction, transaction_id)
    if not db_trans:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Проверяем новые user / category / account
    user = session.get(User, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cat = session.get(Category, data.category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    old_account_id = db_trans.account_id
    old_amount = db_trans.amount

    # 1) Если раньше был счёт, "возвращаем" старую сумму 
    #    (обнуляем то, что мы добавляли/убирали из этого счёта)
    if old_account_id is not None:
        old_acc = session.get(Account, old_account_id)
        if old_acc:
            old_acc.balance -= old_amount
            session.add(old_acc)

    # 2) Обновляем поля транзакции
    db_trans.user_id = data.user_id
    db_trans.category_id = data.category_id
    db_trans.account_id = data.account_id
    db_trans.amount = data.amount
    db_trans.description = data.description

    # 3) Если теперь указан новый счёт, добавляем новую сумму
    if data.account_id is not None:
        new_acc = session.get(Account, data.account_id)
        if not new_acc:
            raise HTTPException(status_code=404, detail="Account not found")
        new_acc.balance += data.amount
        session.add(new_acc)

    session.add(db_trans)
    session.commit()
    session.refresh(db_trans)
    return db_trans


@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, session: Session = Depends(get_session)):
    """
    Удаляем транзакцию. Если она была привязана к счёту, 
    компенсируем (убираем) её из баланса этого счёта.
    """
    db_trans = session.get(Transaction, transaction_id)
    if not db_trans:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Возвращаем баланс счёта к состоянию до этой транзакции
    if db_trans.account_id is not None:
        account = db_trans.account
        if account:
            account.balance -= db_trans.amount
            session.add(account)

    session.delete(db_trans)
    session.commit()
    return {"ok": True}