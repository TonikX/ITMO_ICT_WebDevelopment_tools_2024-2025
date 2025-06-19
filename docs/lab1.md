# Hackathon Management System API Documentation

## Описание системы
Система для организации и проведения хакатонов с функционалом:
- Регистрация участников
- Формирование команд
- Публикация задач
- Оценка работ

## Сущности системы

### 1. Пользователь (User)
**Поля:**
- `id` - уникальный идентификатор
- `name` - имя пользователя
- `email` - электронная почта (уникальное)
- `phone` - контактный телефон
- `skills` - навыки (строка)

### 2. Команда (Team)
**Поля:**
- `id` - уникальный идентификатор
- `name` - название команды
- `description` - описание команды

### 3. Задача (Task)
**Поля:**
- `id` - уникальный идентификатор
- `description` - описание задачи
- `requirements` - требования
- `evaluation_criteria` - критерии оценки

### 4. Работа (Work)
**Поля:**
- `id` - уникальный идентификатор
- `task_id` - ID задачи
- `team_id` - ID команды
- `file` - ссылка на файл работы

### 5. Оценка (Evaluation)
**Поля:**
- `id` - уникальный идентификатор
- `work_id` - ID работы
- `score` - баллы
- `feedback` - обратная связь

```
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Annotated
from typing_extensions import TypedDict
from connection import get_session, init_db
from models import User, Team, UserTeam, Task, Work, Evaluation, TaskDefault, TeamDefault, UserDefault, WorkDefault

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/users", response_model=List[User])
def read_users(session: Session = Depends(get_session)):

    return session.exec(select(User)).all()

@app.get("/teams", response_model=List[Team])
def get_teams(session: Session = Depends(get_session)):

    return session.exec(select(Team)).all()

@app.get("/tasks", response_model=List[Task])
def get_tasks(session: Session = Depends(get_session)):

    return session.exec(select(Task)).all()

@app.get("/works", response_model=List[Work])
def get_works(session: Session = Depends(get_session)):

    return session.exec(select(Work)).all()

@app.get("/user/{user_id}", response_model=User)
def get_user(user_id: int, session: Session = Depends(get_session)):

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/team/{team_id}", response_model=Team)
def get_team(team_id: int, session: Session = Depends(get_session)):

    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@app.get("/work/{work_id}", response_model=Work)
def get_work(work_id: int, session: Session = Depends(get_session)):

    work = session.get(Work, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="work not found")
    return work

@app.get("/task/{task_id}", response_model=Task)
def get_task(task_id: int, session: Session = Depends(get_session)):

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/user")
def create_user(user: UserDefault, session: Session = Depends(get_session)) -> TypedDict('Response', {"status": int, "data": User}):
    user = Task.model_validate(user)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"status": 200, "data": user}


@app.post("/team")
def create_team(team: TeamDefault, session: Session = Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Team}):
    team = Task.model_validate(team)
    session.add(team)
    session.commit()
    session.refresh(team)
    return {"status": 200, "data": team}

@app.post("/work")
def create_team(work: WorkDefault, session: Session = Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Work}):
    work = Task.model_validate(work)
    session.add(work)
    session.commit()
    session.refresh(work)
    return {"status": 200, "data": work}


@app.post("/task")
def create_task(task: TaskDefault, session: Session = Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Task}):

    task = Task.model_validate(task)
    session.add(task)
    session.commit()
    session.refresh(task)
    return {"status": 200, "data": task}

@app.patch("/user{user_id}")
def user_update(user_id: int, user: UserDefault, session=Depends(get_session)) -> UserDefault:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")
    user_data = user.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.patch("/work{work_id}")
def work_update(work_id: int, work: WorkDefault, session=Depends(get_session)) -> WorkDefault:
    db_work = session.get(User, work_id)
    if not db_work:
        raise HTTPException(status_code=404, detail="work not found")
    work_data = work.model_dump(exclude_unset=True)
    for key, value in work_data.items():
        setattr(db_work, key, value)
    session.add(db_work)
    session.commit()
    session.refresh(db_work)
    return db_work


@app.patch("/task{task_id}")
def task_update(task_id: int, task: TaskDefault, session=Depends(get_session)) -> TaskDefault:
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="task not found")
    task_data = task.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(db_task, key, value)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@app.patch("/team{team_id}")
def team_update(team_id: int, team: TeamDefault, session=Depends(get_session)) -> TeamDefault:
    db_team = session.get(Team, team_id)
    if not db_team:
        raise HTTPException(status_code=404, detail="team not found")
    team_data = team.model_dump(exclude_unset=True)
    for key, value in team_data.items():
        setattr(db_team, key, value)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team

@app.delete("/user/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}


@app.delete("/team/{team_id}")
def delete_team(team_id: int, session: Session = Depends(get_session)):

    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team)
    session.commit()
    return {"ok": True}

@app.delete("/task/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session)):

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}

@app.delete("/work/{work_id}")
def delete_work(work_id: int, session: Session = Depends(get_session)):

    work = session.get(Work, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="work not found")
    session.delete(work)
    session.commit()
    return {"ok": True}
```

```
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DB_URL')

if not db_url:
    raise ValueError("DB_URL не установлен в .env файле")

engine = create_engine(db_url, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```
