from fastapi import FastAPI, HTTPException, Path, status
from typing import List

from models import Warrior, Profession, Skill, RaceType

app = FastAPI()

# Временная БД
warriors_db: List[Warrior] = [
    Warrior(id=1, race=RaceType.worker, name="Ivan", level=5,
            profession=Profession(id=1, title="Blacksmith", description="Works with metals"),
            skills=[Skill(id=1, name="Forge", description="Can forge weapons")]),
    Warrior(id=2, race=RaceType.junior, name="Olga", level=2,
            profession=None,
            skills=[]),
]

professions_db: List[Profession] = [
    Profession(id=1, title="Blacksmith", description="Works with metals"),
    Profession(id=2, title="Archer", description="Skilled with bow"),
]

# --- CRUD для Warrior ---

@app.get("/warriors", response_model=List[Warrior])
def get_warriors() -> List[Warrior]:
    return warriors_db

@app.get("/warrior/{warrior_id}", response_model=Warrior)
def get_warrior(
    warrior_id: int = Path(..., description="ID воина, которого нужно получить", ge=1)
) -> Warrior:
    for w in warriors_db:
        if w.id == warrior_id:
            return w
    raise HTTPException(status_code=404, detail="Warrior not found")

@app.post("/warrior", response_model=Warrior, status_code=status.HTTP_201_CREATED)
def create_warrior(warrior: Warrior) -> Warrior:
    if any(w.id == warrior.id for w in warriors_db):
        raise HTTPException(status_code=400, detail="ID already exists")
    warriors_db.append(warrior)
    return warrior

@app.put("/warrior/{warrior_id}", response_model=Warrior)
def update_warrior(
    warrior_id: int,
    warrior: Warrior
) -> Warrior:
    for idx, w in enumerate(warriors_db):
        if w.id == warrior_id:
            warriors_db[idx] = warrior
            return warrior
    raise HTTPException(status_code=404, detail="Warrior not found")

@app.delete("/warrior/{warrior_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_warrior(warrior_id: int):
    for idx, w in enumerate(warriors_db):
        if w.id == warrior_id:
            warriors_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Warrior not found")

# --- CRUD для Profession ---

@app.get("/professions", response_model=List[Profession])
def get_professions() -> List[Profession]:
    return professions_db

@app.get("/profession/{profession_id}", response_model=Profession)
def get_profession(profession_id: int = Path(..., ge=1)) -> Profession:
    for p in professions_db:
        if p.id == profession_id:
            return p
    raise HTTPException(status_code=404, detail="Profession not found")

@app.post("/profession", response_model=Profession, status_code=status.HTTP_201_CREATED)
def create_profession(profession: Profession) -> Profession:
    if any(p.id == profession.id for p in professions_db):
        raise HTTPException(status_code=400, detail="ID already exists")
    professions_db.append(profession)
    return profession

@app.put("/profession/{profession_id}", response_model=Profession)
def update_profession(profession_id: int, profession: Profession) -> Profession:
    for idx, p in enumerate(professions_db):
        if p.id == profession_id:
            professions_db[idx] = profession
            return profession
    raise HTTPException(status_code=404, detail="Profession not found")

@app.delete("/profession/{profession_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profession(profession_id: int):
    for idx, p in enumerate(professions_db):
        if p.id == profession_id:
            professions_db.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Profession not found")