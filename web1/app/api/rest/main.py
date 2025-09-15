from fastapi import FastAPI
from sqlmodel import SQLModel
from database import engine

from app.api.rest.routers.v1.user_router import router as user_router
from app.api.rest.routers.v1.teams import router as teams_router
from app.api.rest.routers.v1.hackathons import router as hackathons_router
from app.api.rest.routers.v1.tasks import router as tasks_router
from app.api.rest.routers.v1.submissions import router as submissions_router

app = FastAPI()


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


app.include_router(user_router)
app.include_router(teams_router)
app.include_router(hackathons_router)
app.include_router(tasks_router)
app.include_router(submissions_router)
