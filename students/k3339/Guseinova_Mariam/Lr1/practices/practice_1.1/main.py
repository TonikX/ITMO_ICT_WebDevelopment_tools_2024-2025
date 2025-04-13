from fastapi import FastAPI, HTTPException
from models import Warrior, Profession
from typing import List
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

# Временная база данных для профессий
temp_professions_bd = [
    {"id": 1, "title": "Влиятельный человек", "description": "Эксперт по всем вопросам"},
    {"id": 2, "title": "Дельфист-гребец", "description": "Уважаемый сотрудник"},
    {"id": 3, "title": "Программист", "description": "Создает программное обеспечение"}
]


@app.get("/")
def hello():
    return "Hello, [username]!"


@app.get("/warriors_list")
def warriors_list() -> List[Warrior]:
    return temp_bd


@app.get("/warrior/{warrior_id}")
def warriors_get(warrior_id: int) -> List[Warrior]:
    return [warrior for warrior in temp_bd if warrior.get("id") == warrior_id]


@app.post("/warrior")
def warriors_create(warrior: Warrior) -> TypedDict('Response', {"status": int, "data": Warrior}):
    warrior_to_append = warrior.model_dump()
    temp_bd.append(warrior_to_append)
    return {"status": 200, "data": warrior}


@app.delete("/warrior/delete{warrior_id}")
def warrior_delete(warrior_id: int):
    for i, warrior in enumerate(temp_bd):
        if warrior.get("id") == warrior_id:
            temp_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/warrior{warrior_id}")
def warrior_update(warrior_id: int, warrior: Warrior) -> List[Warrior]:
    for war in temp_bd:
        if war.get("id") == warrior_id:
            warrior_to_append = warrior.model_dump()
            temp_bd.remove(war)
            temp_bd.append(warrior_to_append)
    return temp_bd


# API для профессий
@app.get("/professions")
def get_professions() -> List[Profession]:
    return temp_professions_bd


@app.get("/professions/{profession_id}")
def get_profession(profession_id: int) -> Profession:
    for profession in temp_professions_bd:
        if profession.get("id") == profession_id:
            return Profession(**profession)
    raise HTTPException(status_code=404, detail="Profession not found")


@app.post("/professions")
def create_profession(profession: Profession) -> TypedDict('Response', {"status": int, "data": Profession}):
    profession_to_append = profession.model_dump()
    temp_professions_bd.append(profession_to_append)
    return {"status": 201, "data": profession}


@app.delete("/professions/{profession_id}")
def delete_profession(profession_id: int):
    for i, profession in enumerate(temp_professions_bd):
        if profession.get("id") == profession_id:
            temp_professions_bd.pop(i)
            return {"status": 200, "message": f"Profession with id {profession_id} deleted"}
    raise HTTPException(status_code=404, detail="Profession not found")


@app.put("/professions/{profession_id}")
def update_profession(profession_id: int, profession: Profession) -> Profession:
    for i, prof in enumerate(temp_professions_bd):
        if prof.get("id") == profession_id:
            profession_to_update = profession.model_dump()
            temp_professions_bd[i] = profession_to_update
            return Profession(**profession_to_update)
    raise HTTPException(status_code=404, detail="Profession not found")
