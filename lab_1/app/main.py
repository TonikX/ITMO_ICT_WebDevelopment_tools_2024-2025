from fastapi import FastAPI, HTTPException, Depends
from typing import List
from sqlmodel import Session, select
from models import Category, Transaction, Tag, TransactionType
from db import engine, init_db, get_session
from datetime import date
from auth import router as auth_router

app = FastAPI()
app.include_router(auth_router)



@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/categories", response_model=List[Category])
def read_categories(session: Session = Depends(get_session)):
    categories = session.exec(select(Category)).all()
    return categories

@app.post("/categories", response_model=Category)
def create_category(category: Category, session: Session = Depends(get_session)):
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@app.get("/categories/{category_id}", response_model=Category)
def read_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.delete("/categories/{category_id}")
def delete_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return {"ok": True}


@app.get("/tags", response_model=List[Tag])
def read_tags(session: Session = Depends(get_session)):
    tags = session.exec(select(Tag)).all()
    return tags

@app.post("/tags", response_model=Tag)
def create_tag(tag: Tag, session: Session = Depends(get_session)):
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag

@app.get("/tags/{tag_id}", response_model=Tag)
def read_tag(tag_id: int, session: Session = Depends(get_session)):
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@app.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, session: Session = Depends(get_session)):
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    session.delete(tag)
    session.commit()
    return {"ok": True}


@app.get("/transactions", response_model=List[Transaction])
def read_transactions(session: Session = Depends(get_session)):
    transactions = session.exec(select(Transaction)).all()
    return transactions

@app.post("/transactions", response_model=Transaction)
def create_transaction(transaction: Transaction, session: Session = Depends(get_session)):
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction

@app.get("/transactions/{transaction_id}", response_model=Transaction)
def read_transaction(transaction_id: int, session: Session = Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@app.patch("/transactions/{transaction_id}", response_model=Transaction)
def update_transaction(transaction_id: int, transaction_update: Transaction, session: Session = Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    update_data = transaction_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(transaction, key, value)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction

@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, session: Session = Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(transaction)
    session.commit()
    return {"ok": True}


@app.get("/report")
def financial_report(session: Session = Depends(get_session)):
    transactions = session.exec(select(Transaction)).all()
    total_income = sum(t.amount for t in transactions if t.type == TransactionType.income)
    total_expense = sum(t.amount for t in transactions if t.type == TransactionType.expense)
    balance = total_income - total_expense
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance
    }
