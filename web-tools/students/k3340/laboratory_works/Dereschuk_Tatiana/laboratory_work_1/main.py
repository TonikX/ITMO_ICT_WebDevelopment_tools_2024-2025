from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from db.connection import init_db
from endpoints.project_endpoints import project_router
from endpoints.skill_endpoints import skill_router
from endpoints.team_endpoints import team_router
from endpoints.team_member_endpoints import team_member_router
from endpoints.user_endpoints import user_router
from endpoints.user_skills_endpoints import user_skill_router
from model import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(skill_router, prefix="/skills", tags=["skills"])
app.include_router(project_router, prefix="/projects", tags=["projects"])
app.include_router(team_router, prefix="/teams", tags=["teams"])
app.include_router(team_member_router, prefix="/members", tags=["members"])
app.include_router(user_skill_router, prefix="/user/skills", tags=["user_skills"])

if __name__ == '__main__':
    uvicorn.run('main:app', host="localhost", port=8000, reload=True)
