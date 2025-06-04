from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from typing import List
from connection import init_db, get_session
from models import *

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/users", response_model=User)
def create_user(user: UserBase, session=Depends(get_session)):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.get("/users", response_model=List[User])
def get_users(session=Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, session=Depends(get_session)):
    user = session.get(User, user_id)
    return user

@app.post("/transactions", response_model=Transaction)
def create_transaction(transaction: TransactionBase, session=Depends(get_session)):
    db_transaction = Transaction.model_validate(transaction)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction

@app.post("/user/{user_id}/transaction", response_model=User)
def add_transaction(user_id: int, transaction: Transaction):
    for user in temp_db:
        if user.get("id") == user_id:
            user["transactions"].append(transaction.dict())
            return user

@app.post("/budgets", response_model=Budget)
def create_budget(budget: BudgetBase, session=Depends(get_session)):
    db_budget = Budget.model_validate(budget)
    session.add(db_budget)
    session.commit()
    session.refresh(db_budget)
    return db_budget

@app.get("/users/{user_id}/budgets", response_model=List[Budget])
def get_user_budgets(user_id: int, session=Depends(get_session)):
    budgets = session.exec(select(Budget).where(Budget.user_id == user_id)).all()
    return budgets

@app.post("/goals", response_model=Goal)
def create_goal(goal: GoalBase, session=Depends(get_session)):
    db_goal = Goal.model_validate(goal)
    session.add(db_goal)
    session.commit()
    session.refresh(db_goal)
    return db_goal

@app.get("/users/{user_id}/notifications", response_model=List[Notification])
def get_user_notifications(user_id: int, session=Depends(get_session)):
    notifications = session.exec(select(Notification).where(Notification.user_id == user_id)).all()
    return notifications