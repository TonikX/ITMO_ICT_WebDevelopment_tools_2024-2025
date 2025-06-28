from fastapi import FastAPI, Depends
from sqlmodel import Session
from models import *
from connection import engine, get_session, init_db
from typing import List
from sqlalchemy import *

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/warriors", response_model=List[Warrior])
def get_warriors(session: Session = Depends(get_session)):
    return session.exec(select(Warrior)).all()

@app.get("/warriors/{warrior_id}", response_model=Warrior)
def get_warrior(warrior_id: int, session: Session = Depends(get_session)):
    return session.get(Warrior, warrior_id)

@app.post("/warriors")
def create_warrior(warrior: Warrior, session: Session = Depends(get_session)):
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return warrior

@app.put("/warriors/{warrior_id}")
def update_warrior(warrior_id: int, warrior: Warrior, session: Session = Depends(get_session)):
    db_warrior = session.get(Warrior, warrior_id)
    for key, value in warrior.dict().items():
        setattr(db_warrior, key, value)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior

@app.delete("/warriors/{warrior_id}")
def delete_warrior(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    session.delete(warrior)
    session.commit()
    return {"ok": True}


