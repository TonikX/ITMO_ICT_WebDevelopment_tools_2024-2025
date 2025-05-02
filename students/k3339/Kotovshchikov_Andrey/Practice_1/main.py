from typing import List
from fastapi import FastAPI

from models import Profession, Warrior

app = FastAPI()


professions = [
    {
        "id": 1,
        "title": "Инженер-схемотехник",
        "description": "Паяет схемы",
    }
]

temp_bd = [
    {
        "id": 1,
        "race": "director",
        "name": "Мартынов Дмитрий",
        "level": 12,
        "profession": {
            "id": 1,
            "title": "Влиятельный человек",
            "description": "Эксперт по всем вопросам",
        },
        "skills": [
            {"id": 1, "name": "Купле-продажа компрессоров", "description": ""},
            {"id": 2, "name": "Оценка имущества", "description": ""},
        ],
    },
    {
        "id": 2,
        "race": "worker",
        "name": "Андрей Косякин",
        "level": 12,
        "profession": {
            "id": 1,
            "title": "Дельфист-гребец",
            "description": "Уважаемый сотрудник",
        },
        "skills": [],
    },
]


@app.get("/")
def hello():
    return "Hello, Andrey!"


@app.get("/warriors_list")
def warriors_list() -> List[Warrior]:
    return temp_bd


@app.get("/warrior/{warrior_id}")
def warriors_get(warrior_id: int) -> List[Warrior]:
    return [warrior for warrior in temp_bd if warrior.get("id") == warrior_id]


@app.post("/warrior")
def warriors_create(warrior: Warrior):
    warrior_to_append = warrior.model_dump()
    temp_bd.append(warrior_to_append)
    return {"status": 200, "data": warrior}


@app.delete("/warrior/{warrior_id}")
def warrior_delete(warrior_id: int):
    for i, warrior in enumerate(temp_bd):
        if warrior.get("id") == warrior_id:
            temp_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/warrior/{warrior_id}")
def warrior_update(warrior_id: int, warrior: Warrior) -> List[Warrior]:
    for war in temp_bd:
        if war.get("id") == warrior_id:
            warrior_to_append = warrior.model_dump()
            temp_bd.remove(war)
            temp_bd.append(warrior_to_append)
    return temp_bd


@app.get("/professions")
def profession_list() -> List[Profession]:
    return professions


@app.post("/professions")
def profession_create(profession: Profession):
    profession_dict = profession.model_dump()
    professions.append(profession_dict)
    return {"status": 201, "data": profession}


@app.put("/professions/{profession_id}")
def profession_update(profession_id: int, profession: Profession):
    for prof in professions:
        if prof.get("id") == profession_id:
            profession_dict = profession.model_dump()
            professions.remove(prof)
            professions.append(profession_dict)

    return {"status": 201, "data": profession}


@app.delete("/professions/{profession_id}")
def profession_delete(profession_id: int):
    for prof in professions:
        if prof.get("id") == profession_id:
            professions.remove(prof)
            break

    return {"status": 201, "data": "deleted"}
