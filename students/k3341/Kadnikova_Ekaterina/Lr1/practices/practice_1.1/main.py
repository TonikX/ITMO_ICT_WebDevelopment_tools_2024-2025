from fastapi import FastAPI
from models import Warrior
from typing import List
from typing_extensions import TypedDict

temp_db = [
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
    },
]

app = FastAPI()

@app.get("/")
def hello():
    return "Hello, User!"

@app.get("/warriors_list", response_model=List[Warrior])
def warriors_list():
    return temp_db

@app.get("/warrior/{warrior_id}")
def warrior_get(warrior_id: int) -> Warrior | None:
    for warrior in temp_db:
        if warrior["id"] == warrior_id:
            return warrior
    return None

class Response(TypedDict):
    status: int
    data: Warrior

@app.post("/warrior", response_model=Response)
def warrior_create(warrior: Warrior):
    temp_db.append(warrior.model_dump())
    return {"status": 200, "data": warrior}

@app.delete("/warrior/{warrior_id}")
def warrior_delete(warrior_id: int):
    global temp_db
    temp_db = [warrior for warrior in temp_db if warrior["id"] != warrior_id]
    return {"message": f"Warrior with id {warrior_id} deleted"}

@app.put("/warrior/{warrior_id}", response_model=List[Warrior])
def warrior_update(warrior_id: int, warrior: Warrior):
    for i, war in enumerate(temp_db):
        if war["id"] == warrior_id:
            temp_db[i] = warrior.model_dump()
    return temp_db