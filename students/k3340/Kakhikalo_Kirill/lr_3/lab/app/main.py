import os
from datetime import datetime
from typing import List
from uuid import UUID
from fastapi import FastAPI, HTTPException, Depends
from pydantic import SecretStr
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from celery import Celery
from celery.result import AsyncResult

import connections
import security
import auth
from model import User, Account, Category, Transaction, Budget, Target
from schemas import (UserCreate, UserRead, AccountCreate, AccountRead, CategoryCreate, CategoryRead, TransactionRead,
                     Token, TransactionWrite, BudgetRead, BudgetCreate, TargetCreate, TargetRead)

app = FastAPI()

get_db = connections.get_session

broker_url = os.getenv("CELERY_BROKER_URL")
backend_url = os.getenv("CELERY_RESULT_BACKEND")
celery = Celery("app_tasks", broker=broker_url, backend=backend_url)


@app.on_event("startup")
def on_startup():
    connections.init_db()


@app.post("/token", response_model=Token)
def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db),
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
def read_users_me(current_user=Depends(auth.get_current_user)):
    return current_user


@app.get("/users", response_model=List[UserRead])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@app.post("/users", response_model=UserRead, status_code=201)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    new_user = User(username=user_in.username, email=user_in.email,
                    hashed_password=security.hash_password(user_in.password.get_secret_value()))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/users/change_password", response_model=UserRead, status_code=200)
def change_password(new_password: SecretStr, current_user=Depends(auth.get_current_user),
                    db: Session = Depends(get_db)):
    current_user.hashed_password = security.hash_password(new_password.get_secret_value())
    db.commit()
    db.refresh(current_user)
    return current_user


@app.get("/accounts", response_model=List[AccountRead])
def get_all_accounts(current_user=Depends(auth.get_current_user)):
    return current_user.accounts


@app.get("/accounts/{account_id}", response_model=AccountRead)
def get_account_by_id(account_id: UUID, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == current_user.id)
        .first()
    )
    if not account:
        raise HTTPException(404, "Account not found")
    return account


@app.post("/accounts", response_model=AccountRead, status_code=201)
def create_account(acct_in: AccountCreate, current_user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    new_acct = Account(
        user_id=current_user.id,
        name=acct_in.name,
        balance=acct_in.balance,
        currency=acct_in.currency,
    )
    db.add(new_acct)
    db.commit()
    db.refresh(new_acct)
    return new_acct


@app.post("/categories", response_model=CategoryRead, status_code=201)
def create_category(cat_in: CategoryCreate, db: Session = Depends(get_db)):
    new_cat = Category(name=cat_in.name, description=cat_in.description)
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return new_cat


@app.get("/categories", response_model=List[CategoryRead])
def get_all_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@app.get("/accounts/{account_id}/transactions", response_model=List[TransactionRead])
def get_transactions_by_account(
        account_id: UUID, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)
):
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == current_user.id)
        .first()
    )
    if not account:
        raise HTTPException(404, "Account not found")
    return account.transactions


@app.post("/accounts/{account_id}/transactions", response_model=TransactionRead, status_code=201)
def create_transaction(account_id: UUID, transaction_in: TransactionWrite, db: Session = Depends(get_db),
                       current_user=Depends(auth.get_current_user)):
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == current_user.id)
        .first()
    )
    if not account:
        raise HTTPException(404, "Account not found")

    new_transaction = Transaction(
        account_id=account.id,
        amount=transaction_in.amount,
        timestamp=datetime.utcnow(),
        category_id=transaction_in.category_id,
        description=transaction_in.description
    )

    if account.balance + transaction_in.amount < 0:
        raise HTTPException(400, "Not enough money")

    db.add(new_transaction)
    account.balance += transaction_in.amount
    db.commit()
    db.refresh(new_transaction)
    return new_transaction


@app.get("/budgets", response_model=List[BudgetRead], status_code=200)
def read_budgets(db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    budgets = (
        db.query(Budget)
        .join(Account)
        .filter(Account.user_id == current_user.id)
        .all()
    )

    return budgets


@app.post("/budgets", response_model=BudgetRead, status_code=201)
def create_budget(budget_in: BudgetCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(auth.get_current_user)):
    account = db.get(Account, budget_in.account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(404, "Account not found")

    new_budget = Budget(
        account_id=budget_in.account_id,
        limit=budget_in.limit,
        start_date=budget_in.start_date,
        end_date=budget_in.end_date,
    )
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    return new_budget


@app.delete("/budgets/{budget_id}", status_code=200)
def delete_budget(budget_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    budget = db.query(Budget).get(budget_id)
    if not budget or budget.account.user_id != current_user.id:
        raise HTTPException(404, "Budget not found")

    db.delete(budget)
    db.commit()
    return


@app.get("/targets", response_model=List[TargetRead], status_code=200)
def read_targets(db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    targets = (
        db.query(Target)
        .join(Account)
        .filter(Account.user_id == current_user.id)
        .all()
    )
    return targets


@app.post("/targets", response_model=TargetRead, status_code=201)
def create_target(target_in: TargetCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(auth.get_current_user)):
    account = db.get(Account, target_in.account_id)
    if not account or account.user_id != current_user.id:
        raise HTTPException(404, "Account not found")

    new_target = Target(
        account_id=target_in.account_id,
        name=target_in.name,
        target_amount=target_in.target_amount,
        deadline=target_in.deadline,
        description=target_in.description,
        created_at=datetime.utcnow()
    )
    db.add(new_target)
    db.commit()
    db.refresh(new_target)
    return new_target


@app.delete("/targets/{target_id}", status_code=200)
def delete_target(target_id: UUID, db: Session = Depends(get_db),
                  current_user: User = Depends(auth.get_current_user), ):
    target = db.query(Target).get(target_id)
    if not target or target.account.user_id != current_user.id:
        raise HTTPException(404, "Target not found")

    db.delete(target)
    db.commit()
    return


@app.post("/schedule-parse")
async def schedule_parse(url: str):
    task = celery.send_task("main.parse_url", args=[url])
    return {"task_id": task.id}


@app.get("/parse-result/{task_id}")
async def parse_result(task_id: str):
    res = AsyncResult(task_id, app=celery)
    if res.ready():
        return {"status": res.status, "result": res.result}
    else:
        return {"status": res.status}
