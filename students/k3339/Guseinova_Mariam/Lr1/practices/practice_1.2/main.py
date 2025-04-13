from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlmodel import Session, select

from connection import get_session, init_db
from models import Warrior, WarriorDefault, Profession, ProfessionDefault, Skill, WarriorProfessions

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


# API для профессий
@app.post("/professions/", response_model=Profession)
def create_profession(profession: ProfessionDefault, session: Session = Depends(get_session)):
    db_profession = Profession.from_orm(profession)
    session.add(db_profession)
    session.commit()
    session.refresh(db_profession)
    return db_profession


@app.get("/professions/", response_model=List[Profession])
def read_professions(session: Session = Depends(get_session)):
    professions = session.exec(select(Profession)).all()
    return professions


@app.get("/professions/{profession_id}", response_model=Profession)
def read_profession(profession_id: int, session: Session = Depends(get_session)):
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    return profession


@app.put("/professions/{profession_id}", response_model=Profession)
def update_profession(profession_id: int, profession: ProfessionDefault, session: Session = Depends(get_session)):
    db_profession = session.get(Profession, profession_id)
    if not db_profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    profession_data = profession.dict(exclude_unset=True)
    updated_profession = db_profession.copy(update=profession_data)
    session.add(updated_profession)
    session.commit()
    session.refresh(updated_profession)
    return updated_profession


@app.delete("/professions/{profession_id}", response_model=dict)
def delete_profession(profession_id: int, session: Session = Depends(get_session)):
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    session.delete(profession)
    session.commit()
    return {"ok": True}


# API для скиллов
@app.post("/skills/", response_model=Skill)
def create_skill(skill: Skill, session: Session = Depends(get_session)):
    db_skill = Skill.from_orm(skill)
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return db_skill


@app.get("/skills/", response_model=List[Skill])
def read_skills(session: Session = Depends(get_session)):
    skills = session.exec(select(Skill)).all()
    return skills


@app.get("/skills/{skill_id}", response_model=Skill)
def read_skill(skill_id: int, session: Session = Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@app.put("/skills/{skill_id}", response_model=Skill)
def update_skill(skill_id: int, skill: Skill, session: Session = Depends(get_session)):
    db_skill = session.get(Skill, skill_id)
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    skill_data = skill.dict(exclude_unset=True)
    updated_skill = db_skill.copy(update=skill_data)
    session.add(updated_skill)
    session.commit()
    session.refresh(updated_skill)
    return updated_skill


@app.delete("/skills/{skill_id}", response_model=dict)
def delete_skill(skill_id: int, session: Session = Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    session.delete(skill)
    session.commit()
    return {"ok": True}


# API для воинов
@app.post("/warriors/", response_model=WarriorProfessions)
def create_warrior(warrior: WarriorDefault, session: Session = Depends(get_session)):
    db_warrior = Warrior.from_orm(warrior)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior


@app.get("/warriors/", response_model=List[WarriorProfessions])
def read_warriors(session: Session = Depends(get_session)):
    warriors = session.exec(select(Warrior)).all()
    return warriors


@app.get("/warriors/{warrior_id}", response_model=WarriorProfessions)
def read_warrior(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior


@app.put("/warriors/{warrior_id}", response_model=WarriorProfessions)
def update_warrior(warrior_id: int, warrior: WarriorDefault, session: Session = Depends(get_session)):
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    warrior_data = warrior.dict(exclude_unset=True)
    updated_warrior = db_warrior.copy(update=warrior_data)
    session.add(updated_warrior)
    session.commit()
    session.refresh(updated_warrior)
    return updated_warrior


@app.delete("/warriors/{warrior_id}", response_model=dict)
def delete_warrior(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"ok": True}


# API для добавления и удаления скиллов у воина
@app.post("/warriors/{warrior_id}/skills/{skill_id}/", response_model=WarriorProfessions)
def add_skill_to_warrior(warrior_id: int, skill_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    skill = session.get(Skill, skill_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    warrior.skills.append(skill)
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return warrior


@app.delete("/warriors/{warrior_id}/skills/{skill_id}/", response_model=WarriorProfessions)
def remove_skill_from_warrior(warrior_id: int, skill_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    skill = session.get(Skill, skill_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    warrior.skills.remove(skill)
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return warrior
