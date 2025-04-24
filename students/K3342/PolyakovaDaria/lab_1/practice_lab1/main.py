from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlmodel import select
from models import Warrior, WarriorDefault, Profession, WarriorWithSkills, Skill
from practice_1.connection import init_db, get_session
from sqlmodel import Session

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


# ——— WARRIOR CRUD ———

@app.get("/warriors_list", response_model=List[WarriorWithSkills])
def warriors_list(session: Session = Depends(get_session)):
    return session.exec(select(Warrior)).all()


@app.get("/warrior/{warrior_id}", response_model=WarriorWithSkills)
def warrior_get(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior


@app.post("/warrior")
def warrior_create(warrior: WarriorDefault, session: Session = Depends(get_session)):
    warrior_db = Warrior.model_validate(warrior)
    session.add(warrior_db)
    session.commit()
    session.refresh(warrior_db)
    return {"status": 200, "data": warrior_db}


@app.patch("/warrior/{warrior_id}")
def warrior_update(warrior_id: int, warrior: WarriorDefault, session: Session = Depends(get_session)):
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    data = warrior.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(db_warrior, key, value)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior


@app.delete("/warrior/delete/{warrior_id}")
def warrior_delete(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"ok": True}


# ——— PROFESSION CRUD ———

@app.get("/professions_list")
def professions_list(session: Session = Depends(get_session)):
    return session.exec(select(Profession)).all()


@app.get("/profession/{profession_id}")
def profession_get(profession_id: int, session: Session = Depends(get_session)):
    return session.get(Profession, profession_id)


@app.post("/profession")
def profession_create(prof: Profession, session: Session = Depends(get_session)):
    prof = Profession.model_validate(prof)
    session.add(prof)
    session.commit()
    session.refresh(prof)
    return {"status": 200, "data": prof}


# ——— SKILL CRUD ———

@app.get("/skills_list")
def skills_list(session: Session = Depends(get_session)):
    return session.exec(select(Skill)).all()


@app.get("/skill/{skill_id}")
def skill_get(skill_id: int, session: Session = Depends(get_session)):
    return session.get(Skill, skill_id)


@app.post("/skill")
def skill_create(skill: Skill, session: Session = Depends(get_session)):
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return {"status": 200, "data": skill}
