from fastapi import FastAPI
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel
from fastapi import HTTPException


class RaceType(Enum):
    director = "director"
    worker = "worker"
    junior = "junior"


class Profession(BaseModel):
    id: int
    title: str
    description: str


class Skill(BaseModel):
    id: int
    name: str
    description: str


class Warrior(BaseModel):
    id: int
    race: RaceType
    name: str
    level: int
    profession: Profession
    skills: Optional[List[Skill]] = []

app = FastAPI()


temp_bd = [{
    "id": 1,
    "race": "director",
    "name": "Мартынов Дмитрий",
    "level": 12,
    "profession": {
        "id": 1,
        "title": "Влиятельный человек",
        "description": "Эксперт по всем вопросам"
    },
},
    {
        "id": 2,
        "race": "worker",
        "name": "Андрей Косякин",
        "level": 12,
        "profession": {
            "id": 1,
            "title": "Дельфист-гребец",
            "description": "Уважаемый сотрудник"
        },
    },
]


@app.get("/")
def hello():
    return "Hello, [username]!"


@app.get("/warriors_list")
def warriors_list():
    return temp_bd


@app.get("/warrior/{warrior_id}")
def warriors_list(warrior_id: int):
    return [warrior for warrior in temp_bd if warrior.get("id") == warrior_id]


@app.post("/warrior")
def warriors_list(warrior: dict):
    temp_bd.append(warrior)
    return {"status": 200, "data": warrior}


@app.delete("/warrior/delete{warrior_id}")
def warrior_delete(warrior_id: int):
    for i, warrior in enumerate(temp_bd):
        if warrior.get("id") == warrior_id:
            temp_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/warrior{warrior_id}")
def warrior_update(warrior_id: int, warrior: dict):
    for i, war in enumerate(temp_bd):
        if war.get("id") == warrior_id:
            temp_bd[i] = warrior
    return temp_bd


temp_professions = [
    {
        "id": 1,
        "title": "Влиятельный человек",
        "description": "Эксперт по всем вопросам"
    },
    {
        "id": 2,
        "title": "Дельфист-гребец",
        "description": "Уважаемый сотрудник"
    }
]


@app.get("/professions", response_model=List[Profession])
def get_professions():
    return temp_professions


@app.get("/profession/{profession_id}", response_model=Profession)
def get_profession(profession_id: int):
    profession = next((p for p in temp_professions if p["id"] == profession_id), None)
    if profession is None:
        raise HTTPException(status_code=404, detail="Профессия не найдена")
    return profession


@app.post("/profession", response_model=Profession)
def create_profession(profession: Profession):
    temp_professions.append(profession.dict())
    return profession


@app.delete("/profession/delete/{profession_id}")
def delete_profession(profession_id: int):
    for i, profession in enumerate(temp_professions):
        if profession["id"] == profession_id:
            temp_professions.pop(i)
            return {"status": 200, "message": "Профессия удалена"}
    raise HTTPException(status_code=404, detail="Профессия не найдена")


@app.put("/profession/{profession_id}", response_model=Profession)
def update_profession(profession_id: int, updated_profession: Profession):
    for i, profession in enumerate(temp_professions):
        if profession["id"] == profession_id:
            temp_professions[i] = updated_profession.dict()
            return updated_profession
    raise HTTPException(status_code=404, detail="Профессия не найдена")