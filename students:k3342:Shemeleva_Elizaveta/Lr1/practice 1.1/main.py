from fastapi import FastAPI, HTTPException
from typing import List
from models import Task, TaskCreate, TaskUpdate

app = FastAPI(title="Time Manager")

# Временная бд
temp_db: List[Task] = []
_next_id = 1


@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return temp_db


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    for task in temp_db:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task_in: TaskCreate):
    global _next_id
    task = Task(
        id=_next_id,
        description=task_in.description,
        due_date=task_in.due_date,
        priority=task_in.priority,
        spent_time=0.0
    )
    temp_db.append(task)
    _next_id += 1
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for i, task in enumerate(temp_db):
        if task.id == task_id:
            temp_db.pop(i)
            return
    raise HTTPException(status_code=404, detail="Task not found")


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_in: TaskUpdate):
    for i, task in enumerate(temp_db):
        if task.id == task_id:
            updated = task.copy(update=task_in.dict(exclude_unset=True))
            temp_db[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="Task not found")
