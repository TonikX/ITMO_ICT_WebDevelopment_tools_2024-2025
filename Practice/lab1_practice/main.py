from typing import List

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import joinedload
from sqlmodel import select

from models import Profession, Warrior, WarriorBase, Skill
from connection import init_db, get_session

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/skills_list", response_model=List[Skill])
def skills_list(session=Depends(get_session)):
    return session.exec(select(Skill)).all()

@app.post("/skills", response_model=Skill)
def skills_create(skill: Skill, session=Depends(get_session)):
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill

@app.get("/warriors_list", response_model=List[Warrior])
def warriors_list(session=Depends(get_session)):
    return session.exec(select(Warrior)).all()


@app.get("/warrior/{warrior_id}", response_model=Warrior)
def warriors_get(warrior_id: int, session=Depends(get_session)):
    warrior = session.exec(
        select(Warrior).options(joinedload(Warrior.skills)).where(Warrior.id == warrior_id)
    ).first()

    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior
@app.post("/warrior", response_model=Warrior)
def create_warrior(warrior_data: WarriorBase, session=Depends(get_session)):
    warrior = Warrior(**warrior_data.dict())
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return warrior

@app.patch("/warrior/{warrior_id}", response_model=Warrior)
def warrior_update(warrior_id: int, warrior_data: WarriorBase, session=Depends(get_session)):
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    warrior_data_dict = warrior_data.dict(exclude_unset=True)
    for key, value in warrior_data_dict.items():
        setattr(db_warrior, key, value)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior

@app.delete("/warrior/delete/{warrior_id}")
def warrior_delete(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"ok": True}

@app.get("/professions_list", response_model=List[Profession])
def professions_list(session=Depends(get_session)):
    return session.exec(select(Profession)).all()

@app.post("/profession", response_model=Profession)
def profession_create(profession: Profession, session=Depends(get_session)):
    session.add(profession)
    session.commit()
    session.refresh(profession)
    return profession
