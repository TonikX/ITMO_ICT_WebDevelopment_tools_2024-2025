from fastapi import FastAPI, HTTPException
from typing import List
from models import Profession, Warrior
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


def get_all_professions():
    professions = []
    for warrior in temp_bd:
        profession = warrior.get("profession")
        if profession not in professions and profession:
            professions.append(profession)
    return professions


def get_profession_by_id(profession_id: int):
    professions = get_all_professions()
    for profession in professions:
        if profession.get("id") == profession_id:
            return profession
    return None


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


@app.delete("/warrior/delete/{warrior_id}")
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


@app.get("/professions/")
def professions_list() -> List[Profession]:
    return get_all_professions()


@app.get("/professions/{profession_id}")
def profession_get(profession_id: int) -> Profession:
    profession = get_profession_by_id(profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    return profession


@app.post("/professions")
def profession_create(profession: Profession) -> TypedDict('Response', {"status": int, "data": Profession}):
    existing_profession = get_profession_by_id(profession.id)
    if existing_profession:
        raise HTTPException(status_code=400, detail="Profession with this ID already exists")

    new_warrior = {
        "id": len(temp_bd) + 1,
        "race": "junior",
        "name": f"Воин с профессией {profession.title}",
        "level": 1,
        "profession": profession.model_dump(),
        "skills": []
    }
    temp_bd.append(new_warrior)

    return {"status": 200, "data": profession}


@app.put("/professions/{profession_id}")
def profession_update(profession_id: int, profession: Profession) -> List[Warrior]:
    old_profession = get_profession_by_id(profession_id)
    if not old_profession:
        raise HTTPException(status_code=404, detail="Profession not found")

    for warrior in temp_bd:
        if warrior.get("profession", {}).get("id") == profession_id:
            warrior["profession"] = profession.model_dump()

    return temp_bd


@app.delete("/professions/{profession_id}")
def profession_delete(profession_id: int):
    profession = get_profession_by_id(profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")

    default_profession = {
        "id": 0,
        "title": "Без профессии",
        "description": "Профессия удалена"
    }

    for warrior in temp_bd:
        if warrior.get("profession", {}).get("id") == profession_id:
            warrior["profession"] = default_profession

    return {"status": 201, "message": "Profession deleted"}