from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import List



from models import Work, User, Task, Team
from connection import get_session, init_db


app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()



class ParseRequest(BaseModel):
    urls: List[str]

# @app.post("/async-parse")
# async def parse_async(urls: list[str]):
#     if not urls:
#         raise HTTPException(status_code=400, detail="Не передано ни одного URL")
#
#     start_time = datetime.now()
#
#     try:
#         result = await async_parse(urls)
#         end_time = datetime.now()
#         duration = (end_time - start_time).total_seconds()
#
#         return {
#             "status": "Завершено",
#             "processed_urls": urls,
#             "result": result,
#             "execution_time_seconds": round(duration, 2)
#         }
#     except Exception as e:
#         end_time = datetime.now()
#         duration = (end_time - start_time).total_seconds()
#         raise HTTPException(
#             status_code=500,
#             detail=f"Ошибка при парсинге: {str(e)}, время выполнения: {round(duration, 2)} сек."
#         )
#
# @app.post("/multi-parse")
# def parse_multi(urls: List[str]):
#     if not urls:
#         raise HTTPException(status_code=400, detail="Не передано ни одного URL")
#
#     start_time = datetime.now()
#
#     try:
#         multi_parse(urls)
#         end_time = datetime.now()
#         duration = (end_time - start_time).total_seconds()
#
#         return {
#             "status": "Завершено",
#             "processed_urls": urls,
#             "execution_time_seconds": round(duration, 2)
#         }
#     except Exception as e:
#         end_time = datetime.now()
#         duration = (end_time - start_time).total_seconds()
#         raise HTTPException(
#             status_code=500,
#             detail=f"Ошибка при парсинге: {str(e)}, время выполнения: {round(duration, 2)} сек."
#         )
#
# @app.post("/thread-parse")
# def parse_thread(urls: List[str]):
#     if not urls:
#         raise HTTPException(status_code=400, detail="Не передано ни одного URL")
#
#     start_time = datetime.now()
#
#     try:
#         thread_parse(urls)
#         end_time = datetime.now()
#         duration = (end_time - start_time).total_seconds()
#
#         return {
#             "status": "Завершено",
#             "processed_urls": urls,
#             "execution_time_seconds": round(duration, 2)
#         }
#     except Exception as e:
#         end_time = datetime.now()
#         duration = (end_time - start_time).total_seconds()
#         raise HTTPException(
#             status_code=500,
#             detail=f"Ошибка при парсинге: {str(e)}, время выполнения: {round(duration, 2)} сек."
#         )
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
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@app.get("/team/{team_id}", response_model=Team)
def get_team(team_id: int, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    return team


@app.get("/work/{work_id}", response_model=Work)
def get_work(work_id: int, session: Session = Depends(get_session)):
    work = session.get(Work, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Работа не найдена")
    return work


@app.get("/task/{task_id}", response_model=Task)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task



from models import UserDefault, TeamDefault, TaskDefault, WorkDefault
from typing import TypedDict


class ResponseUser(TypedDict):
    status: int
    data: User


@app.post("/user", response_model=ResponseUser)
def create_user(user: UserDefault, session: Session = Depends(get_session)):
    db_user = User(**user.model_dump())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"status": 200, "data": db_user}


@app.post("/team", response_model=ResponseUser)
def create_team(team: TeamDefault, session: Session = Depends(get_session)):
    db_team = Team(**team.model_dump())
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return {"status": 200, "data": db_team}


@app.post("/work", response_model=ResponseUser)
def create_work(work: WorkDefault, session: Session = Depends(get_session)):
    db_work = Work(**work.model_dump())
    session.add(db_work)
    session.commit()
    session.refresh(db_work)
    return {"status": 200, "data": db_work}


@app.post("/task", response_model=ResponseUser)
def create_task(task: TaskDefault, session: Session = Depends(get_session)):
    db_task = Task(**task.model_dump())
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return {"status": 200, "data": db_task}