from fastapi import FastAPI
from db import *
from routing.user_router import router as user_router
from routing.hackathon_router import router as hackathon_router
from routing.team_router import router as team_router
from routing.task_router import router as task_router
from routing.submission_router import router as submission_router

# uvicorn app:app --port 8000
# alembic revision --autogenerate -m "change "
# alembic upgrade head
# mkdocs serve
# mkdocs gh-deploy


app = FastAPI()


app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(team_router, prefix="/team", tags=["team"])
app.include_router(hackathon_router, prefix="/hackathon", tags=["hackathon"])
app.include_router(task_router, prefix="/task", tags=["task"])
app.include_router(submission_router, prefix="/submission", tags=["submission"])


@app.on_event("startup")
def on_startup():
    init_db()