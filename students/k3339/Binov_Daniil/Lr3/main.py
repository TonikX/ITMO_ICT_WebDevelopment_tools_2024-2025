from fastapi import FastAPI
from app.connection import init_db
from app.routers import tasks, categories, time_logs, schedules, users, auth
from celery_app import app as celery_app

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(tasks.router)
app.include_router(categories.router)
app.include_router(time_logs.router)
app.include_router(schedules.router)
app.include_router(users.router)
app.include_router(auth.router)