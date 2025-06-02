from fastapi import FastAPI, Depends
from models import *
from connection import *

from typing_extensions import TypedDict

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()
    
    
@app.post("/users")
def user_create(user: User, 
                session=Depends(get_session)) -> TypedDict('Response', 
                                                           {"status": int,
                                                            "data": User}):
    user = User.model_validate(user)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"status": 200, "data": user}

@app.get("/user_list")
def users_list(session=Depends(get_session)) -> List[User]:
    return session.exec(select(User)).all()


@app.get("/user/{user_id}")
def users_get(user_id: int, session=Depends(get_session)) -> User:
    return session.exec(select(User).where(User.id == user_id)).first()

@app.get("/task/{task_id}", response_model=TaskUser)
def tasks_get(task_id: int, session=Depends(get_session)) -> Task:
    task = session.get(Task, task_id)
    return task

@app.get("/task_sc/{task_sc_id}", response_model=Task_Schedule_Serializator)
def tasks_sc_get(task_sc_id: int, session=Depends(get_session)) -> Task_Schedule:
    task_sc = session.get(Task_Schedule, task_sc_id)
    return task_sc