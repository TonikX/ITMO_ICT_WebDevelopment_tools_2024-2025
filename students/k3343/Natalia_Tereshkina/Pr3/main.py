from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from connection import init_db, get_session
from models import *

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def hello():
    return "Wellcome, Personal Finance"

@app.get("/users", response_model=List[User])
def get_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@app.get("/user/{user_id}", response_model=User)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/user", response_model=User)
def add_user(user: UserBase, session: Session = Depends(get_session)):
    # Check if username or email already exists
    existing_user = session.exec(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.delete("/user/delete/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    session.delete(user)
    session.commit()
    return {"status": 200, "message": "User deleted"}

@app.put("/user/{user_id}", response_model=User)
def update_user(user_id: int, user: UserBase, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if new username or email conflicts with other users
    if user.username != db_user.username or user.email != db_user.email:
        existing_user = session.exec(
            select(User).where(
                ((User.username == user.username) | (User.email == user.email)) &
                (User.id != user_id)
            )
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Username or email already exists")
    
    user_data = user.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.post("/transaction", response_model=Transaction)
def create_transaction(transaction: TransactionBase, session: Session = Depends(get_session)):
    db_transaction = Transaction.model_validate(transaction)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction

@app.post("/user/{user_id}/transaction", response_model=Transaction)
def add_transaction(user_id: int, transaction: TransactionBase, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_transaction = Transaction.model_validate(transaction)
    db_transaction.user_id = user_id
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction

@app.post("/budget", response_model=Budget)
def create_budget(budget: BudgetBase, session: Session = Depends(get_session)):
    db_budget = Budget.model_validate(budget)
    session.add(db_budget)
    session.commit()
    session.refresh(db_budget)
    return db
