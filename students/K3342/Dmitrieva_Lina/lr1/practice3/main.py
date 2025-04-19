from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy import select
from typing import List
from models import User, Transaction, UserCreate, TransactionCreate, UserWithTransactions, TransactionWithUser
from db.connection import get_session, init_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/users", response_model=User)
def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    # Проверяем, существует ли уже пользователь с таким email
    stmt = select(User).where(User.email == user_data.email)
    existing_user = session.exec(stmt).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    db_user = User.model_validate(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


# Создание транзакции
@app.post("/transactions", response_model=Transaction)
def create_transaction(
        transaction_data: TransactionCreate,
        session: Session = Depends(get_session)
):
    # Проверяем, существует ли пользователь
    user = session.get(User, transaction_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {transaction_data.user_id} not found"
        )

    db_transaction = Transaction.model_validate(transaction_data)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


# Получение всех пользователей
@app.get("/users", response_model=List[User])
def get_users(session: Session = Depends(get_session)):
    stmt = select(User)
    users = session.exec(stmt).all()
    return users

# Получение пользователя по id
@app.patch("/users/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# Получение транзацкии по id
@app.patch("/transactions/{transaction_id}", response_model=Transaction)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionCreate,
    session: Session = Depends(get_session)
):
    db_transaction = session.get(Transaction, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    update_data = transaction_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_transaction, key, value)

    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


# Получение транзакций пользователя
@app.get("/transactions/{user_id}", response_model=List[Transaction])
def get_transactions(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    stmt = select(Transaction).where(Transaction.user_id == user_id)
    transactions = session.exec(stmt).all()
    return transactions

@app.get("/users/{user_id}/detailed", response_model=UserWithTransactions)
def get_user_detailed(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/transaction/{transaction_id}/detailed", response_model=TransactionWithUser)
def get_transaction_detailed(transaction_id: int, session: Session = Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}

@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, session: Session = Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(transaction)
    session.commit()
    return {"ok": True}
