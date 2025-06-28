from fastapi import FastAPI
from typing import List
from models import Warrior, Profession
from typing_extensions import TypedDict

app = FastAPI()

# Временные "базы данных"
temp_bd = [
    {
        "id": 1,
        "race": "director",
        "name": "Мартынов Дмитрий",
        "level": 12,
        "profession_id": 1,
        "skills": [1, 2],
    },
    {
        "id": 2,
        "race": "worker",
        "name": "Андрей Косякин",
        "level": 12,
        "profession_id": 1,
        "skills": [],
    },
]

profession_temp_bd = [
    {
        "id": 1,
        "title": "работник 1",
        "description": "работник 1",
    },
    {
        "id": 2,
        "title": "работник 2",
        "description": "работник 2",
    },
]


# === Warriors ===
@app.get("/warriors_list")
def warriors_list() -> List[Warrior]:
    return temp_bd


@app.get("/warrior/{warrior_id}")
def get_warrior(warrior_id: int) -> List[Warrior]:
    return [w for w in temp_bd if w.get("id") == warrior_id]


@app.post("/warrior")
def create_warrior(warrior: Warrior) -> TypedDict('Response', {"status": int, "data": Warrior}):
    warrior_dict = warrior.model_dump()
    temp_bd.append(warrior_dict)
    return {"status": 200, "data": warrior}


@app.delete("/warrior/delete/{warrior_id}")
def delete_warrior(warrior_id: int):
    for i, w in enumerate(temp_bd):
        if w.get("id") == warrior_id:
            temp_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}


# === Professions ===
@app.get("/professions_list")
def professions_list() -> List[Profession]:
    return profession_temp_bd


@app.get("/profession/{profession_id}")
def get_profession(profession_id: int) -> List[Profession]:
    return [p for p in profession_temp_bd if p.get("id") == profession_id]


@app.post("/profession")
def create_profession(profession: Profession) -> TypedDict('Response', {"status": int, "data": Profession}):
    profession_dict = profession.model_dump()
    profession_temp_bd.append(profession_dict)
    return {"status": 200, "data": profession}


@app.delete("/profession/delete/{profession_id}")
def delete_profession(profession_id: int):
    for i, p in enumerate(profession_temp_bd):
        if p.get("id") == profession_id:
            profession_temp_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}