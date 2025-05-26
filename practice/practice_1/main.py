from typing import List
from typing_extensions import TypedDict
from fastapi import FastAPI, HTTPException
from models import Warrior, Profession, RaceType, Skill

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
        "skills": [
            {
                "id": 1,
                "name": "Купле-продажа компрессоров",
                "description": ""
            },
            {
                "id": 2,
                "name": "Оценка имущества",
                "description": ""
            }
        ]
    },
    {
        "id": 2,
        "race": "worker",
        "name": "Андрей Косякин",
        "level": 12,
        "profession": {
            "id": 2,
            "title": "Дельфист-гребец",
            "description": "Уважаемый сотрудник"
        },
        "skills": []
    },
]

professions_db = [
    {
        "id": 1,
        "title": "Влиятельный человек",
        "description": "Эксперт по всем вопросам"
    },
    {
        "id": 2,
        "title": "Дельфист-гребец",
        "description": "Уважаемый сотрудник"
    },
]


@app.get("/", tags=["Root"])
def hello():
    return "Hello, [username]!"

@app.get("/warriors_list", response_model=List[Warrior], tags=["Воины"])
def warriors_list() -> List[Warrior]:
    return temp_bd

@app.get("/warrior/{warrior_id}", response_model=List[Warrior], tags=["Воины"])
def warriors_get(warrior_id: int) -> List[Warrior]:
    warrior = [warrior for warrior in temp_bd if warrior.get("id") == warrior_id]
    if not warrior:
        raise HTTPException(status_code=404, detail="Воин не найден")
    return warrior

@app.post("/warrior", response_model=Warrior, tags=["Воины"])
def warriors_create(warrior: Warrior) -> TypedDict('Response', {"status": int, "data": Warrior}):
    warrior_to_append = warrior.model_dump()
    temp_bd.append(warrior_to_append)
    return {"status": 200, "data": warrior}

@app.delete("/warrior/delete{warrior_id}", tags=["Воины"])
def warrior_delete(warrior_id: int):
    for i, warrior in enumerate(temp_bd):
        if warrior.get("id") == warrior_id:
            temp_bd.pop(i)
            return {"status": 201, "message": "deleted"}
    raise HTTPException(status_code=404, detail="Воин не найден")

@app.put("/warrior{warrior_id}", response_model=List[Warrior], tags=["Воины"])
def warrior_update(warrior_id: int, warrior: Warrior) -> List[Warrior]:
    for war in temp_bd:
        if war.get("id") == warrior_id:
            warrior_to_append = warrior.model_dump()
            temp_bd.remove(war)
            temp_bd.append(warrior_to_append)
            return temp_bd
    raise HTTPException(status_code=404, detail="Воин не найден")

@app.get("/professions", tags=["Профессии"])
def get_professions() -> List[Profession]:
    return professions_db

@app.get("/profession/{profession_id}", tags=["Профессии"])
def get_profession(profession_id: int) -> Profession:
    prof = next((p for p in professions_db if p.get("id") == profession_id), None)
    if not prof:
        raise HTTPException(status_code=404, detail="Профессия не найдена")
    return prof

@app.post("/profession", tags=["Профессии"])
def create_profession(profession: Profession) -> TypedDict('Response', {"status": int, "data": Profession}):
    profession_to_append = profession.model_dump()
    professions_db.append(profession_to_append)
    return {"status": 200, "data": profession}

@app.put("/profession/{profession_id}", tags=["Профессии"])
def update_profession(profession_id: int, profession: Profession) -> Profession:
    for index, prof in enumerate(professions_db):
        if prof.get("id") == profession_id:
            professions_db[index] = profession.model_dump()
            return profession
    raise HTTPException(status_code=404, detail="Профессия не найдена")

@app.delete("/profession/{profession_id}", tags=["Профессии"])
def delete_profession(profession_id: int):
    for index, prof in enumerate(professions_db):
        if prof.get("id") == profession_id:
            professions_db.pop(index)
            return {"status": 201, "message": "Профессия удалена"}
    raise HTTPException(status_code=404, detail="Профессия не найдена")
