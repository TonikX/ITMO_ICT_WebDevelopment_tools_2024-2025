from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlmodel import Session, select

# Твои файлы
from connection import get_session, init_db
from models import Warrior, Profession, Skill, WarriorDefault, WarriorProfessions

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


# === Профессии ===
@app.post("/profession/", response_model=Profession)
def create_profession(profession: Profession, session: Session = Depends(get_session)):
    session.add(profession)
    session.commit()
    session.refresh(profession)
    return profession


@app.get("/professions/", response_model=List[Profession])
def list_professions(session: Session = Depends(get_session)):
    return session.exec(select(Profession)).all()


@app.get("/profession/{profession_id}", response_model=Profession)
def get_profession(profession_id: int, session: Session = Depends(get_session)):
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    return profession


# === Воины ===
@app.post("/warrior/", response_model=Warrior)
def create_warrior(warrior: WarriorDefault, session: Session = Depends(get_session)):
    db_warrior = Warrior.model_validate(warrior)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior


@app.get("/warriors/", response_model=List[Warrior])
def list_warriors(session: Session = Depends(get_session)):
    return session.exec(select(Warrior)).all()


@app.get("/warrior/{warrior_id}", response_model=WarriorProfessions)
def get_warrior(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior


@app.patch("/warrior/{warrior_id}")
def update_warrior(warrior_id: int, warrior_data: WarriorDefault, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")

    update_data = warrior_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(warrior, key, value)

    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return warrior


@app.delete("/warrior/{warrior_id}")
def delete_warrior(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"ok": True}


# === Навыки ===
@app.post("/skill/", response_model=Skill)
def create_skill(skill: Skill, session: Session = Depends(get_session)):
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


@app.get("/skills/", response_model=List[Skill])
def list_skills(session: Session = Depends(get_session)):
    return session.exec(select(Skill)).all()


@app.get("/skill/{skill_id}", response_model=Skill)
def get_skill(skill_id: int, session: Session = Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill