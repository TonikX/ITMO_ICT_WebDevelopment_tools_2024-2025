from fastapi import FastAPI
from database import init_db
from routers import tasks

app = FastAPI(title="Time Manager")

@app.on_event("startup")
def on_startup():
    init_db()

# подключаем роутер
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
