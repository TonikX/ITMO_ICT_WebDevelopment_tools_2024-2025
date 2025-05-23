from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from connection import init_db, get_session
from models import Warrior, WarriorBase, Profession, ProfessionBase, Skill, SkillBase, WarriorWithFullDetails


app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/warriors", response_model=List[WarriorWithFullDetails])
def read_warriors(session: Session = Depends(get_session)):
    return session.exec(select(Warrior)).all()

@app.get("/warrior/{warrior_id}", response_model=WarriorWithFullDetails)
def read_warrior(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior

@app.post("/warrior", response_model=Warrior, status_code=201)
def create_warrior(warrior: Warrior, session: Session = Depends(get_session)):
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return warrior

@app.post("/warrior/{warrior_id}/add_skill/{skill_id}")
def add_skill_to_warrior(warrior_id: int, skill_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    if skill in warrior.skills:
        raise HTTPException(status_code=400, detail="Skill is already linked to the warrior")

    warrior.skills.append(skill)
    session.commit()
    session.refresh(warrior)

    return {"status": 200, "message": f"Skill '{skill.name}' added to warrior '{warrior.name}'"}


@app.patch("/warrior/{warrior_id}", response_model=Warrior)
def update_warrior(warrior_id: int, warrior_data: WarriorBase, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    update_data = warrior_data.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(warrior, field, val)
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return warrior

@app.delete("/warrior/{warrior_id}", status_code=204)
def delete_warrior(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()

@app.get("/professions", response_model=List[Profession])
def read_professions(session: Session = Depends(get_session)):
    return session.exec(select(Profession)).all()

@app.get("/profession/{profession_id}", response_model=Profession)
def read_profession(profession_id: int, session: Session = Depends(get_session)):
    prof = session.get(Profession, profession_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profession not found")
    return prof

@app.post("/profession", response_model=Profession, status_code=201)
def create_profession(prof: Profession, session: Session = Depends(get_session)):
    session.add(prof)
    session.commit()
    session.refresh(prof)
    return prof

@app.patch("/profession/{profession_id}", response_model=Profession)
def update_profession(profession_id: int, prof_data: ProfessionBase, session: Session = Depends(get_session)):
    prof = session.get(Profession, profession_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profession not found")
    update_data = prof_data.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(prof, field, val)
    session.add(prof)
    session.commit()
    session.refresh(prof)
    return prof

@app.delete("/profession/{profession_id}", status_code=204)
def delete_profession(profession_id: int, session: Session = Depends(get_session)):
    prof = session.get(Profession, profession_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profession not found")
    session.delete(prof)
    session.commit()

@app.get("/skills", response_model=List[Skill])
def read_skills(session: Session = Depends(get_session)):
    return session.exec(select(Skill)).all()

@app.get("/skill/{skill_id}", response_model=Skill)
def read_skill(skill_id: int, session: Session = Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@app.post("/skill", response_model=Skill, status_code=201)
def create_skill(skill: Skill, session: Session = Depends(get_session)):
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill

@app.patch("/skill/{skill_id}", response_model=Skill)
def update_skill(skill_id: int, skill_data: SkillBase, session: Session = Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    update_data = skill_data.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(skill, field, val)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill

@app.delete("/skill/{skill_id}", status_code=204)
def delete_skill(skill_id: int, session: Session = Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    session.delete(skill)
    session.commit()