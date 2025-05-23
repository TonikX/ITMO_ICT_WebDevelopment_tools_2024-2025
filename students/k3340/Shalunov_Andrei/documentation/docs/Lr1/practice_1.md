# Практика 1.1 — Создание базового приложения на FastAPI

## Модели данных

**Warrior**
```
class Warrior(BaseModel):
    id: int
    race: RaceType
    name: str
    level: int
    profession: Profession
    skills: Optional[List[Skill]] = []
```
**Profession** 
```
class Profession(BaseModel):
    id: int
    title: str
    description: str
```
**Skill** 
```
class Skill(BaseModel):
    id: int
    name: str
    description: str
```
**RaceType**
```
class RaceType(str, Enum):
    director = "director"
    worker   = "worker"
    junior   = "junior"
```

## API Endpoints

**Управление воинами**
```
GET /warriors_list - Получить список всех воинов
GET /warrior/{warrior_id} - Получить информацию о конкретном воине
POST /warrior - Создать нового воина
PUT /warrior{warrior_id} - Обновить информацию о воине
DELETE /warrior/delete{warrior_id} - Удалить воина
```

**Управление профессиями**
```
GET /professions - Получить список всех профессий
GET /profession/{profession_id} - Получить информацию о конкретной профессии
POST /profession - Создать новую профессию
PUT /profession/{profession_id} - Обновить информацию о профессии
DELETE /profession/{profession_id} - Удалить профессию
```

## Исходный код
**main.py**
```
from fastapi import FastAPI, HTTPException
from typing import List
from models import Warrior, Profession, Skill, RaceType

app = FastAPI()

temp_warriors = [
{
    "id": 1,
    "race": RaceType.director,
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
    "race": RaceType.worker,
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
    {"id": 2, "title": "Дельфист-гребец", "description": "Уважаемый сотрудник"},
]

@app.get("/warriors_list", response_model=List[Warrior])
def warriors_list():
    return temp_warriors

@app.get("/warrior/{warrior_id}", response_model=Warrior)
def warrior_get(warrior_id: int):
    for w in temp_warriors:
        if w["id"] == warrior_id:
            return w
    raise HTTPException(status_code=404, detail="Warrior not found")

@app.post("/warrior", response_model=Warrior, status_code=201)
def warrior_create(warrior: Warrior):
    temp_warriors.append(warrior.dict())
    return warrior

@app.put("/warrior/{warrior_id}", response_model=Warrior)
def warrior_update(warrior_id: int, warrior: Warrior):
    for idx, w in enumerate(temp_warriors):
        if w["id"] == warrior_id:
            temp_warriors[idx] = warrior.dict()
            return warrior
    raise HTTPException(status_code=404, detail="Warrior not found")

@app.delete("/warrior/{warrior_id}", status_code=204)
def warrior_delete(warrior_id: int):
    for idx, w in enumerate(temp_warriors):
        if w["id"] == warrior_id:
            temp_warriors.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Warrior not found")


@app.get("/professions", response_model=List[Profession])
def professions_list():
    return temp_professions

@app.get("/profession/{prof_id}", response_model=Profession)
def profession_get(prof_id: int):
    for p in temp_professions:
        if p["id"] == prof_id:
            return p
    raise HTTPException(status_code=404, detail="Profession not found")

@app.post("/profession", response_model=Profession, status_code=201)
def profession_create(prof: Profession):
    temp_professions.append(prof.dict())
    return prof

@app.put("/profession/{prof_id}", response_model=Profession)
def profession_update(prof_id: int, prof: Profession):
    for idx, p in enumerate(temp_professions):
        if p["id"] == prof_id:
            temp_professions[idx] = prof.dict()
            return prof
    raise HTTPException(status_code=404, detail="Profession not found")

@app.delete("/profession/{prof_id}", status_code=204)
def profession_delete(prof_id: int):
    for idx, p in enumerate(temp_professions):
        if p["id"] == prof_id:
            temp_professions.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Profession not found")
```