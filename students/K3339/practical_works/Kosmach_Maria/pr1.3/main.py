from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select, delete
from typing_extensions import TypedDict

from connection import init_db, get_session
from models import Warrior, Profession, WarriorDefault, WarriorDetails, ProfessionDefault, SkillDefault, Skill, \
    SkillWarriorLink


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def hello():
    return "Hello, [username]!"


@app.get("/warriors_list", response_model=List[WarriorDetails])
def warriors_list(session=Depends(get_session)) -> List[Warrior]:
    return session.exec(select(Warrior)).scalars().all()


@app.get("/warrior/{warrior_id}", response_model=WarriorDetails)
def warriors_get(warrior_id: int, session=Depends(get_session)) -> Warrior:
    warrior = session.get(Warrior, warrior_id)
    return warrior


@app.post("/warrior")
def warriors_create(warrior: WarriorDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                                     "data": Warrior}):
    warrior = Warrior.model_validate(warrior)
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return {"status": 201, "data": warrior}


@app.delete("/warrior/delete/{warrior_id}")
def warrior_delete(warrior_id: int, session=Depends(get_session)):
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(db_warrior)
    session.commit()
    return {"status": 204, "message": "deleted"}


@app.patch("/warrior/{warrior_id}", response_model=WarriorDefault)
def warrior_update(warrior_id: int, warrior: WarriorDefault, session=Depends(get_session)) -> WarriorDefault:
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    warrior_data = warrior.model_dump(exclude_unset=True)
    for key, value in warrior_data.items():
        if key == "skill_ids":
            session.exec(delete(SkillWarriorLink).where(SkillWarriorLink.warrior_id == warrior_id))
            for skill_id in warrior_data["skill_ids"]:
                session.add(SkillWarriorLink(warrior_id=warrior_id, skill_id=skill_id))
        else:
            setattr(db_warrior, key, value)

    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior


@app.get("/professions_list", response_model=List[ProfessionDefault])
def professions_list(session=Depends(get_session)) -> List[Profession]:
    return session.exec(select(Profession)).scalars().all()


@app.get("/profession/{profession_id}", response_model=ProfessionDefault)
def profession_get(profession_id: int, session=Depends(get_session)) -> Profession:
    return session.get(Profession, profession_id)


@app.post("/profession")
def profession_create(prof: ProfessionDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                                       "data": Profession}):
    prof = Profession.model_validate(prof)
    session.add(prof)
    session.commit()
    session.refresh(prof)
    return {"status": 201, "data": prof}


@app.delete("/profession/delete/{profession_id}")
def profession_delete(profession_id: int, session=Depends(get_session)):
    db_profession = session.get(Profession, profession_id)
    if not db_profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    session.delete(db_profession)
    session.commit()
    return {"status": 204, "message": "deleted"}


@app.patch("/profession/{profession_id}", response_model=ProfessionDefault)
def profession_update(profession_id: int, profession: ProfessionDefault,
                      session=Depends(get_session)) -> ProfessionDefault:
    db_profession = session.get(Profession, profession_id)
    print(profession)
    if not db_profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    profession_data = profession.model_dump(exclude_unset=True)
    for key, value in profession_data.items():
        setattr(db_profession, key, value)
    session.add(db_profession)
    session.commit()
    session.refresh(db_profession)
    return db_profession


@app.get("/skills_list", response_model=List[SkillDefault])
def skills_list(session=Depends(get_session)) -> List[Skill]:
    return session.exec(select(Skill)).scalars().all()


@app.get("/skill/{skill_id}", response_model=SkillDefault)
def skill_get(skill_id: int, session=Depends(get_session)):
    return session.get(Skill, skill_id)


@app.post("/skill")
def skill_create(skill: SkillDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,
                                                                                              "data": Skill}):
    skill = Skill.model_validate(skill)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return {"status": 201, "data": skill}


@app.delete("/skill/delete/{skill_id}")
def skill_delete(skill_id: int, session=Depends(get_session)):
    db_skill = session.get(Skill, skill_id)
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    session.delete(db_skill)
    session.commit()
    return {"status": 204, "message": "deleted"}


@app.patch("/skill/{skill_id}", response_model=SkillDefault)
def skill_update(skill_id: int, skill: SkillDefault, session=Depends(get_session)) -> SkillDefault:
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
