from fastapi import FastAPI, Depends, HTTPException
from typing import List, Optional
from sqlmodel import select, Session
from models import *
from connection import get_session, init_db
from typing_extensions import TypedDict

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.on_event("startup")
def on_startup():
    init_db()


# Воины
@app.post("/warrior", response_model=Warrior)
def warriors_create(warrior: WarriorDefault, session: Session = Depends(get_session)):
    db_warrior = Warrior.model_validate(warrior)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior


@app.get("/warriors", response_model=List[Warrior])
def warriors_list(session: Session = Depends(get_session)):
    warriors = session.exec(select(Warrior)).all()
    return warriors


@app.get("/warrior/{warrior_id}", response_model=WarriorFull)
def warrior_get(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior


@app.patch("/warrior/{warrior_id}", response_model=Warrior)
def warrior_update(warrior_id: int, warrior: WarriorDefault, session: Session = Depends(get_session)):
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    warrior_data = warrior.model_dump(exclude_unset=True)
    for key, value in warrior_data.items():
        setattr(db_warrior, key, value)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior


@app.delete("/warrior/{warrior_id}")
def warrior_delete(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"ok": True}


# Профессии
@app.post("/profession", response_model=Profession)
def profession_create(prof: ProfessionDefault, session: Session = Depends(get_session)):
    db_prof = Profession.model_validate(prof)
    session.add(db_prof)
    session.commit()
    session.refresh(db_prof)
    return db_prof


@app.get("/professions", response_model=List[Profession])
def professions_list(session: Session = Depends(get_session)):
    professions = session.exec(select(Profession)).all()
    return professions


@app.get("/profession/{profession_id}", response_model=Profession)
def profession_get(profession_id: int, session: Session = Depends(get_session)):
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    return profession


@app.patch("/profession/{profession_id}", response_model=Profession)
def profession_update(profession_id: int, prof: ProfessionDefault, session: Session = Depends(get_session)):
    db_prof = session.get(Profession, profession_id)
    if not db_prof:
        raise HTTPException(status_code=404, detail="Profession not found")
    prof_data = prof.model_dump(exclude_unset=True)
    for key, value in prof_data.items():
        setattr(db_prof, key, value)
    session.add(db_prof)
    session.commit()
    session.refresh(db_prof)
    return db_prof


@app.delete("/profession/{profession_id}")
def profession_delete(profession_id: int, session: Session = Depends(get_session)):
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    session.delete(profession)
    session.commit()
    return {"ok": True}


# Умения
@app.post("/skill", response_model=Skill)
def skill_create(skill: SkillDefault, session: Session = Depends(get_session)):
    db_skill = Skill.model_validate(skill)
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return db_skill


@app.get("/skills", response_model=List[Skill])
def skills_list(session: Session = Depends(get_session)):
    skills = session.exec(select(Skill)).all()
    return skills


@app.get("/skill/{skill_id}", response_model=Skill)
def skill_get(skill_id: int, session: Session = Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@app.patch("/skill/{skill_id}", response_model=Skill)
def skill_update(skill_id: int, skill: SkillDefault, session: Session = Depends(get_session)):
    db_skill = session.get(Skill, skill_id)
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    skill_data = skill.model_dump(exclude_unset=True)
    for key, value in skill_data.items():
        setattr(db_skill, key, value)
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return db_skill


@app.delete("/skill/{skill_id}")
def skill_delete(skill_id: int, session: Session = Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    session.delete(skill)
    session.commit()
    return {"ok": True}


# Связи между воинами и умениями
@app.post("/warrior/{warrior_id}/skill/{skill_id}")
def add_skill_to_warrior(
        warrior_id: int,
        skill_id: int,
        session: Session = Depends(get_session)
):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")

    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    if skill not in warrior.skills:
        warrior.skills.append(skill)
        session.add(warrior)
        session.commit()

    return {"ok": True}


@app.delete("/warrior/{warrior_id}/skill/{skill_id}")
def remove_skill_from_warrior(
        warrior_id: int,
        skill_id: int,
        session: Session = Depends(get_session)
):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")

    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    if skill in warrior.skills:
        warrior.skills.remove(skill)
        session.add(warrior)
        session.commit()

    return {"ok": True}
