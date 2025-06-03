from typing import List
from uuid import UUID
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

import connections
from model import User, Account, Category, Transaction
from schemas import (
    UserCreate, UserRead,
    AccountCreate, AccountRead,
    CategoryCreate, CategoryRead,
    TransactionRead,
)

app = FastAPI()

get_db = connections.get_session

@app.on_event("startup")
def on_startup():
    connections.init_db()

@app.get("/users", response_model=List[UserRead])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/users/{user_id}/accounts", response_model=List[AccountRead])
def get_all_accounts(user_id: UUID, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user.accounts

@app.get("/users/{user_id}/accounts/{account_id}", response_model=AccountRead)
def get_account_by_id(
    user_id: UUID, account_id: UUID, db: Session = Depends(get_db)
):
    account = (
        db.query(Account)
          .filter(Account.id == account_id, Account.user_id == user_id)
          .first()
    )
    if not account:
        raise HTTPException(404, "Account not found")
    return account

@app.get(
    "/users/{user_id}/accounts/{account_id}/transactions",
    response_model=List[TransactionRead],
)
def get_transactions_by_account(
    user_id: UUID, account_id: UUID, db: Session = Depends(get_db)
):
    account = (
        db.query(Account)
          .filter(Account.id == account_id, Account.user_id == user_id)
          .first()
    )
    if not account:
        raise HTTPException(404, "Account not found")
    return account.transactions

@app.post("/users", response_model=UserRead, status_code=201)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    new_user = User(username=user_in.username, email=user_in.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post(
    "/users/{user_id}/accounts",
    response_model=AccountRead,
    status_code=201,
)
def create_account(
    user_id: UUID,
    acct_in: AccountCreate,
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    new_acct = Account(
        user_id=user_id,
        name=acct_in.name,
        balance=acct_in.balance,
        currency=acct_in.currency,
    )
    db.add(new_acct)
    db.commit()
    db.refresh(new_acct)
    return new_acct

@app.post("/categories", response_model=CategoryRead, status_code=201)
def create_category(
    cat_in: CategoryCreate, db: Session = Depends(get_db)
):
    new_cat = Category(name=cat_in.name, description=cat_in.description)
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat
