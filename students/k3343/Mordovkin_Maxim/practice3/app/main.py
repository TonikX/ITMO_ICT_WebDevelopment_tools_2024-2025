from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlmodel import select
from app.connection import init_db, get_session
from app.models import (
    Warrior, WarriorDefault, WarriorResponse,
    Skill, SkillCreate,
    Profession, ProfessionCreate
)



app = FastAPI()


# создание таблиц прис старте, если их пока нет
@app.on_event("startup")
def on_startup():
    init_db()


# ============================================================================

# post запрос на создание warrior
@app.post("/warriors", response_model=WarriorResponse, summary="Создать нового воина")
def create_warrior(warrior: WarriorDefault, session=Depends(get_session)):
    db_warrior = Warrior(**warrior.dict())
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior

# get запрос на получение списка воинов
@app.get("/warriors", response_model=List[WarriorResponse], summary="Получить список всех воинов")
def list_warriors(session=Depends(get_session)):
    return session.exec(select(Warrior)).all()

# get запрос на получения воина по id
@app.get("/warriors/{warrior_id}", response_model=WarriorResponse, summary="Получить воина по ID (с вложенными навыками)")
def get_warrior(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior

# patch запрос для частичного обновления данных
@app.patch("/warriors/{warrior_id}", response_model=WarriorResponse, summary="Частично обновить воина")
def update_warrior(warrior_id: int, warrior: WarriorDefault, session=Depends(get_session)):
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")

    # берём только те поля, что пришли (exclude_unset)
    update_data = warrior.dict(exclude_unset=True)
    for key, val in update_data.items():
        setattr(db_warrior, key, val)

    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior

# запрос на удаление воина
@app.delete("/warriors/{warrior_id}", summary="Удалить воина")
def delete_warrior(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"ok": True}

# ============================================================================

@app.post("/skills", response_model=Skill, summary="Создать новый навык")
def create_skill(skill: SkillCreate, session=Depends(get_session)):
    db_skill = Skill(**skill.dict())
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return db_skill

@app.get("/skills", response_model=List[Skill], summary="Получить все навыки")
def list_skills(session=Depends(get_session)):
    return session.exec(select(Skill)).all()

@app.get("/skills/{skill_id}", response_model=Skill, summary="Получить навык по id")
def get_skill(skill_id: int, session=Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@app.patch("/skills/{skill_id}", response_model=Skill, summary="Обновить навык")
def update_skill( skill_id: int, skill: SkillCreate, session=Depends(get_session)):
    db_skill = session.get(Skill, skill_id)
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    skill_data = skill.dict(exclude_unset=True)
    for key, val in skill_data.items():
        setattr(db_skill, key, val)
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return db_skill

@app.delete("/skills/{skill_id}", summary="Удалить навык")
def delete_skill(skill_id: int, session=Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    session.delete(skill)
    session.commit()
    return {"ok": True}

# ============================================================================

@app.post("/warriors/{warrior_id}/skills/{skill_id}", summary="Привязать навык воину")
def link_skill_to_warrior(warrior_id: int, skill_id:   int, session=    Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    skill   = session.get(Skill, skill_id)
    if not (warrior and skill):
        raise HTTPException(status_code=404, detail="Warrior or Skill not found")

    # orm сам создаст запись в skill_warrior_link
    warrior.skills.append(skill)
    session.add(warrior)
    session.commit()
    return {"ok": True}

@app.delete("/warriors/{warrior_id}/skills/{skill_id}", summary="Отвязать навык от воина")
def unlink_skill_from_warrior(warrior_id: int, skill_id:   int, session=    Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    skill   = session.get(Skill, skill_id)
    if not (warrior and skill):
        raise HTTPException(status_code=404, detail="Warrior or Skill not found")

    warrior.skills.remove(skill)
    session.add(warrior)
    session.commit()
    return {"ok": True}

# ============================================================================

@app.post("/professions", response_model=Profession, summary="Создать профессию")
def create_profession(prof: ProfessionCreate, session=Depends(get_session)):
    db_prof = Profession(**prof.dict())
    session.add(db_prof)
    session.commit()
    session.refresh(db_prof)
    return db_prof

@app.get("/professions", response_model=List[Profession], summary="Список профессий")
def list_professions(session=Depends(get_session)):
    return session.exec(select(Profession)).all()

# ============================================================================



