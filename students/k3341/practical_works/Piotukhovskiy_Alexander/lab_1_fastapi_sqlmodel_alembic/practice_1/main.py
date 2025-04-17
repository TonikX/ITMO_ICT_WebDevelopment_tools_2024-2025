from fastapi import FastAPI, HTTPException
from models import *
import typing as tp
from typing_extensions import TypedDict

app = FastAPI()

temp_bd = [
{
    "id": 1,
    "race": "director",
    "name": "Мартынов Дмитрий",
    "level": 12,
    "profession": {
        "id": 1,
        "title": "Влиятельный человек",
        "description": "Эксперт по всем вопросам"
    },
    "skills":
        [{
            "id": 1,
            "name": "Купле-продажа компрессоров",
            "description": ""

        },
        {
            "id": 2,
            "name": "Оценка имущества",
            "description": ""

        }]
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
    "skills": []
},
]

temp_professions = [
    {"id": 1, "title": "Влиятельный человек", "description": "Эксперт по всем вопросам"},
    {"id": 2, "title": "Дельфист-гребец", "description": "Уважаемый сотрудник"}
]

@app.get("/")
def hello():
    return "Hello, [username]!"


@app.get("/warriors_list")
def warriors_list() -> tp.List[Warrior]:
    return temp_bd


@app.get("/warrior/{warrior_id}")
def warriors_list(warrior_id: int) -> List[Warrior]:
    return [warrior for warrior in temp_bd if warrior.get("id") == warrior_id]


@app.post("/warrior")
def warriors_list(warrior: dict) -> TypedDict('Response', {"status": int, "data": Warrior}):
    temp_bd.append(warrior)
    return {"status": 200, "data": warrior}


@app.put("/warrior{warrior_id}")
def warrior_update(warrior_id: int, warrior: dict) -> List[Warrior]:
    for i, war in enumerate(temp_bd):
        if war.get("id") == warrior_id:
            temp_bd[i] = warrior
    return temp_bd


@app.delete("/warrior/delete{warrior_id}")
def warrior_delete(warrior_id: int):
    for i, warrior in enumerate(temp_bd):
        if warrior.get("id") == warrior_id:
            temp_bd.pop(i)
            break
    return {"status": 200, "message": "deleted"}


@app.get("/professions")
def get_professions() -> tp.List[Profession]:
    return temp_professions

@app.get("/profession/{profession_id}")
def get_profession(profession_id: int) -> Profession:
    for profession in temp_professions:
        if profession.get("id") == profession_id:
            return profession
    raise HTTPException(status_code=404, detail="Профессия не найдена")

@app.post("/profession")
def create_profession(profession: Profession) -> TypedDict('Response', {"status": int, "data": Profession}):
    temp_professions.append(profession.dict())
    return {"status": 200, "data": profession}

@app.put("/profession/{profession_id}")
def update_profession(profession_id: int, profession: Profession) -> tp.List[Profession]:
    for i, prof in enumerate(temp_professions):
        if prof.get("id") == profession_id:
            temp_professions[i] = profession.dict()
            return temp_professions
    raise HTTPException(status_code=404, detail="Профессия не найдена")

@app.delete("/profession/{profession_id}")
def delete_profession(profession_id: int):
    for i, prof in enumerate(temp_professions):
        if prof.get("id") == profession_id:
            temp_professions.pop(i)
            return {"status": 200, "message": "deleted"}
    raise HTTPException(status_code=404, detail="Профессия не найдена")