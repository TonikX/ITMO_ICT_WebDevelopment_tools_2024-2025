from typing import List

from fastapi import FastAPI
from typing_extensions import TypedDict

from models import Warrior, Profession

app = FastAPI()

temp_bd_warriors = [
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

temp_bd_professions = [
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

@app.get("/")
def hello():
    return "Hello, [username]!"


@app.get("/warriors_list")
def warriors_list() -> List[Warrior]:
    return temp_bd_warriors


@app.get("/warrior/{warrior_id}")
def warriors_get(warrior_id: int) -> List[Warrior]:
    return [warrior for warrior in temp_bd_warriors if warrior.get("id") == warrior_id]


@app.post("/warrior")
def warriors_create(warrior: Warrior) -> TypedDict('Response', {"status": int, "data": Warrior}):
    warrior_to_append = warrior.model_dump()
    temp_bd_warriors.append(warrior_to_append)
    return {"status": 200, "data": warrior}


@app.delete("/warrior/delete{warrior_id}")
def warrior_delete(warrior_id: int):
    for i, warrior in enumerate(temp_bd_warriors):
        if warrior.get("id") == warrior_id:
            temp_bd_warriors.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/warrior{warrior_id}")
def warrior_update(warrior_id: int, warrior: Warrior) -> List[Warrior]:
    for war in temp_bd_warriors:
        if war.get("id") == warrior_id:
            warrior_to_append = warrior.model_dump()
            temp_bd_warriors.remove(war)
            temp_bd_warriors.append(warrior_to_append)
    return temp_bd_warriors

@app.get("/professions_list")
def professions_list() -> List[Profession]:
    return temp_bd_professions


@app.get("/professions/{profession_id}")
def professions_get(profession_id: int) -> List[Profession]:
    return [profession for profession in temp_bd_professions if profession.get("id") == profession_id]


@app.post("/profession")
def profession_create(profession: Profession) -> TypedDict('Response', {"status": int, "data": Profession}):
    profession_to_append = profession.model_dump()
    temp_bd_professions.append(profession_to_append)
    return {"status": 200, "data": profession}


@app.delete("/profession/delete/{profession_id}")
def  profession_delete(profession_id: int):
    for i, profession in enumerate(temp_bd_professions):
        if profession.get("id") == profession_id:
            temp_bd_professions.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/profession/{profession_id}")
def profession_update(profession_id: int, profession: Profession) -> List[Profession]:
    for prof in temp_bd_professions:
        if prof.get("id") == profession_id:
            profession_to_append = profession.model_dump()
            temp_bd_professions.remove(prof)
            temp_bd_professions.append(profession_to_append)
    return temp_bd_professions