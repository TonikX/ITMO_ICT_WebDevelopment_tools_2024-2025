from fastapi import FastAPI
from connection import init_db
from routers.user_router import router as user_router
from routers.team_router import router as team_router
from routers.task_router import router as task_router
from routers.submission_router import router as submission_router

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def hello():
    return "Hello, [username]!"


app.include_router(user_router)
app.include_router(team_router)
app.include_router(task_router)
app.include_router(submission_router)
