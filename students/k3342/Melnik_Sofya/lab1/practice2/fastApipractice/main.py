from fastapi import FastAPI, Depends, HTTPException
from typing import List

from sqlmodel import Session, select

from models import Warrior, Skill, Profession
from schemas import WarriorRead, WarriorCreate, SkillRead, SkillCreate, ProfessionRead
from connection import init_db, get_session

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", tags=["Base"])
def root():
    return {"message": "Warrior API is running"}


@app.get("/warriors", response_model=List[WarriorRead])
def get_warriors(session: Session = Depends(get_session)):
    return session.exec(select(Warrior)).all()


@app.get("/warrior/{warrior_id}", response_model=WarriorRead)
def get_warrior(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior


@app.post("/warrior", response_model=WarriorRead)
def create_warrior(warrior_data: WarriorCreate, session: Session = Depends(get_session)):
    db_warrior = Warrior(
        name=warrior_data.name,
        race=warrior_data.race,
        level=warrior_data.level,
        profession_id=warrior_data.profession_id
    )
    if warrior_data.skill_ids:
        skills = session.exec(select(Skill).where(Skill.id.in_(warrior_data.skill_ids))).all()
        db_warrior.skills = skills

    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior


@app.get("/skills", response_model=List[SkillRead])
def read_skills(session: Session = Depends(get_session)):
    return session.exec(select(Skill)).all()


@app.post("/skills", response_model=SkillRead)
def create_skill(skill: SkillCreate, session: Session = Depends(get_session)):
    db_skill = Skill(name=skill.name, description=skill.description)
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return db_skill


@app.get("/professions", response_model=List[ProfessionRead])
def read_professions(session: Session = Depends(get_session)):
    return session.exec(select(Profession)).all()