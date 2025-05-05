from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select
from typing import List, TypedDict

from connection import get_session, init_db
from models import (
    Warrior,
    WarriorDefault,
    Profession,
    ProfessionDefault,
    Skill,
    SkillDefault,
    SkillWarriorLink,
    WarriorWithSkills
)

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/warriors_list")
def warriors_list(session=Depends(get_session)) -> List[Warrior]:
    return session.exec(select(Warrior)).all()


@app.get("/warrior/{warrior_id}", response_model=WarriorWithSkills)
def warriors_get(warrior_id: int, session=Depends(get_session)) -> Warrior:
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior


@app.post("/warrior")
def warriors_create(warrior: WarriorDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                                     "data": Warrior}):
    warrior = Warrior.model_validate(warrior)
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return {"status": 200, "data": warrior}


@app.patch("/warrior/{warrior_id}")
def warrior_update(warrior_id: int, warrior: WarriorDefault, session=Depends(get_session)) -> Warrior:
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
def warrior_delete(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"ok": True}


@app.get("/professions_list")
def professions_list(session=Depends(get_session)) -> List[Profession]:
    return session.exec(select(Profession)).all()


@app.get("/profession/{profession_id}")
def profession_get(profession_id: int, session=Depends(get_session)) -> Profession:
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    return profession


@app.post("/profession")
def profession_create(prof: ProfessionDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                                       "data": Profession}):
    prof = Profession.model_validate(prof)
    session.add(prof)
    session.commit()
    session.refresh(prof)
    return {"status": 200, "data": prof}


@app.patch("/profession/{profession_id}")
def profession_update(profession_id: int, profession: ProfessionDefault, session=Depends(get_session)) -> Profession:
    db_profession = session.get(Profession, profession_id)
    if not db_profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    profession_data = profession.model_dump(exclude_unset=True)
    for key, value in profession_data.items():
        setattr(db_profession, key, value)
    session.add(db_profession)
    session.commit()
    session.refresh(db_profession)
    return db_profession


@app.delete("/profession/{profession_id}")
def profession_delete(profession_id: int, session=Depends(get_session)):
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    session.delete(profession)
    session.commit()
    return {"ok": True}


@app.get("/skills_list")
def skills_list(session=Depends(get_session)) -> List[Skill]:
    return session.exec(select(Skill)).all()


@app.get("/skill/{skill_id}")
def skill_get(skill_id: int, session=Depends(get_session)) -> Skill:
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@app.post("/skill")
def skill_create(skill: SkillDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Skill}):
    skill = Skill.model_validate(skill)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return {"status": 200, "data": skill}


@app.patch("/skill/{skill_id}")
def skill_update(skill_id: int, skill: SkillDefault, session=Depends(get_session)) -> Skill:
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
def skill_delete(skill_id: int, session=Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    session.delete(skill)
    session.commit()
    return {"ok": True}


@app.post("/warrior/{warrior_id}/add_skill/{skill_id}")
def add_skill_to_warrior(warrior_id: int, skill_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")

    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    link = session.exec(
        select(SkillWarriorLink).where(
            SkillWarriorLink.warrior_id == warrior_id,
            SkillWarriorLink.skill_id == skill_id
        )
    ).first()

    if link:
        return {"message": "Skill already assigned to warrior"}

    link = SkillWarriorLink(warrior_id=warrior_id, skill_id=skill_id)
    session.add(link)
    session.commit()

    return {"message": "Skill successfully added to warrior"}


@app.delete("/warrior/{warrior_id}/remove_skill/{skill_id}")
def remove_skill_from_warrior(warrior_id: int, skill_id: int, session=Depends(get_session)):
    link = session.exec(
        select(SkillWarriorLink).where(
            SkillWarriorLink.warrior_id == warrior_id,
            SkillWarriorLink.skill_id == skill_id
        )
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Relationship not found")

    session.delete(link)
    session.commit()

    return {"message": "Skill successfully removed from warrior"}


@app.get("/warrior/{warrior_id}/skills")
def get_warrior_skills(warrior_id: int, session=Depends(get_session)) -> List[Skill]:
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")

    return warrior.skills


@app.get("/skill/{skill_id}/warriors")
def get_skill_warriors(skill_id: int, session=Depends(get_session)) -> List[Warrior]:
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    return skill.warriors
